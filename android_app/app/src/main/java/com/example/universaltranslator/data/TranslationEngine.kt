package com.example.universaltranslator.data

import android.text.Html
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import java.util.regex.Pattern

data class LanguageItem(
    val code: String,
    val nameEn: String,
    val nameVi: String
)

object TranslationEngine {

    val languages = listOf(
        LanguageItem("vi", "Vietnamese", "Tiếng Việt"),
        LanguageItem("en", "English", "Tiếng Anh"),
        LanguageItem("zh-CN", "Chinese (Simplified)", "Tiếng Trung (Giản thể)"),
        LanguageItem("zh-TW", "Chinese (Traditional)", "Tiếng Trung (Phồn thể)"),
        LanguageItem("ja", "Japanese", "Tiếng Nhật"),
        LanguageItem("ko", "Korean", "Tiếng Hàn"),
        LanguageItem("fr", "French", "Tiếng Pháp"),
        LanguageItem("de", "German", "Tiếng Đức"),
        LanguageItem("es", "Spanish", "Tiếng Tây Ban Nha"),
        LanguageItem("ru", "Russian", "Tiếng Nga"),
        LanguageItem("th", "Thai", "Tiếng Thái"),
        LanguageItem("lo", "Lao", "Tiếng Lào"),
        LanguageItem("km", "Khmer", "Tiếng Khmer"),
        LanguageItem("id", "Indonesian", "Tiếng Indonesia"),
        LanguageItem("ms", "Malay", "Tiếng Mã Lai"),
        LanguageItem("it", "Italian", "Tiếng Ý"),
        LanguageItem("pt", "Portuguese", "Tiếng Bồ Đào Nha"),
        LanguageItem("ar", "Arabic", "Tiếng Ả Rập"),
        LanguageItem("hi", "Hindi", "Tiếng Hindi"),
        LanguageItem("tr", "Turkish", "Tiếng Thổ Nhĩ Kỳ")
    )

    private val RESULT_PATTERN: Pattern = Pattern.compile("class=[\"'](?:result-container|t0)[\"']>(.*?)</div>", Pattern.DOTALL)
    private val TAG_PATTERN: Pattern = Pattern.compile("<[^>]+>")

    suspend fun translate(
        text: String,
        targetLang: String,
        sourceLang: String = "auto"
    ): Result<String> = withContext(Dispatchers.IO) {
        try {
            val trimmed = text.trim()
            if (trimmed.isEmpty()) return@withContext Result.success("")
            if (sourceLang == targetLang && sourceLang != "auto") return@withContext Result.success(trimmed)

            val chunks = splitTextIntoChunks(trimmed, 2000)
            val resultBuilder = StringBuilder()

            for ((idx, chunk) in chunks.withIndex()) {
                if (chunk.isBlank()) continue
                val translatedChunk = translateWithFallback(chunk, targetLang, sourceLang)
                if (idx > 0) resultBuilder.append("\n")
                resultBuilder.append(translatedChunk)
            }

            Result.success(resultBuilder.toString())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun translateWithFallback(chunk: String, targetLang: String, sourceLang: String): String {
        // Engine 1: Google Translate Mobile (primary, standard, free, no limits)
        try {
            return translateGoogleMobile(chunk, targetLang, sourceLang)
        } catch (e1: Exception) {
            e1.printStackTrace()
        }

        // Engine 2: MyMemory API (fallback)
        try {
            return translateMyMemory(chunk, targetLang, sourceLang)
        } catch (e2: Exception) {
            e2.printStackTrace()
        }

        throw Exception("Không thể kết nối máy chủ dịch thuật. Vui lòng kiểm tra kết nối mạng (Internet)!")
    }

    /**
     * Primary engine: Google Translate Mobile (deep-translator equivalent)
     */
    private fun translateGoogleMobile(chunk: String, targetLang: String, sourceLang: String): String {
        val encodedText = URLEncoder.encode(chunk, "UTF-8")
        val sl = if (sourceLang.isEmpty()) "auto" else sourceLang
        val urlString = "https://translate.google.com/m?sl=$sl&tl=$targetLang&q=$encodedText"
        val url = URL(urlString)

        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            setRequestProperty("User-Agent", "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
            setRequestProperty("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
            setRequestProperty("Accept-Language", "en-US,en;q=0.9,vi;q=0.8")
            connectTimeout = 12000
            readTimeout = 12000
            instanceFollowRedirects = true
        }

        val htmlContent = conn.inputStream.bufferedReader(Charsets.UTF_8).use { it.readText() }
        val matcher = RESULT_PATTERN.matcher(htmlContent)

        if (matcher.find()) {
            val rawResult = matcher.group(1) ?: ""
            val withoutTags = TAG_PATTERN.matcher(rawResult).replaceAll("")
            return Html.fromHtml(withoutTags, Html.FROM_HTML_MODE_LEGACY).toString().trim()
        }

        throw Exception("Google Translate did not return result container")
    }

    /**
     * Fallback engine: MyMemory API
     */
    private fun translateMyMemory(chunk: String, targetLang: String, sourceLang: String): String {
        val src = if (sourceLang == "auto") "en" else sourceLang
        val pair = "$src|$targetLang"
        val encodedText = URLEncoder.encode(chunk, "UTF-8")
        val urlString = "https://api.mymemory.translated.net/get?q=$encodedText&langpair=$pair"
        val url = URL(urlString)

        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "GET"
            setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            connectTimeout = 10000
            readTimeout = 10000
        }

        val jsonStr = conn.inputStream.bufferedReader(Charsets.UTF_8).use { it.readText() }
        val json = JSONObject(jsonStr)
        val responseData = json.optJSONObject("responseData")
        val translated = responseData?.optString("translatedText")

        if (!translated.isNullOrBlank()) {
            return Html.fromHtml(translated, Html.FROM_HTML_MODE_LEGACY).toString().trim()
        }

        throw Exception("MyMemory API returned empty response")
    }

    private fun splitTextIntoChunks(text: String, maxChars: Int = 2000): List<String> {
        if (text.length <= maxChars) return listOf(text)
        val chunks = mutableListOf<String>()
        val lines = text.split("\n")
        var current = StringBuilder()

        for (line in lines) {
            if (current.length + line.length + 1 <= maxChars) {
                if (current.isNotEmpty()) current.append("\n")
                current.append(line)
            } else {
                if (current.isNotEmpty()) {
                    chunks.add(current.toString())
                    current = StringBuilder()
                }
                if (line.length > maxChars) {
                    for (i in 0 until line.length step maxChars) {
                        chunks.add(line.substring(i, minOf(i + maxChars, line.length)))
                    }
                } else {
                    current.append(line)
                }
            }
        }
        if (current.isNotEmpty()) chunks.add(current.toString())
        return chunks
    }
}
