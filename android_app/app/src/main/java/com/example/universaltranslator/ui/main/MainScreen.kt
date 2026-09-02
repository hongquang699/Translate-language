package com.example.universaltranslator.ui.main

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation3.runtime.NavKey
import com.example.universaltranslator.data.TranslationEngine
import kotlinx.coroutines.launch
import java.io.BufferedReader
import java.io.InputStreamReader

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    onItemClick: (NavKey) -> Unit = {},
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var isVietnamese by remember { mutableStateOf(true) }
    var selectedTab by remember { mutableStateOf(0) } // 0: Text, 1: File

    // Text translation state
    var sourceLangCode by remember { mutableStateOf("auto") }
    var targetLangCode by remember { mutableStateOf("vi") }
    var inputText by remember { mutableStateOf("") }
    var outputText by remember { mutableStateOf("") }
    var isTranslatingText by remember { mutableStateOf(false) }

    // File translation state
    var selectedFileUri by remember { mutableStateOf<Uri?>(null) }
    var selectedFileName by remember { mutableStateOf("") }
    var fileContent by remember { mutableStateOf("") }
    var translatedFileContent by remember { mutableStateOf("") }
    var isTranslatingFile by remember { mutableStateOf(false) }

    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            selectedFileUri = it
            try {
                val cursor = context.contentResolver.query(it, null, null, null, null)
                val nameIndex = cursor?.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME) ?: -1
                if (cursor != null && cursor.moveToFirst() && nameIndex >= 0) {
                    selectedFileName = cursor.getString(nameIndex)
                    cursor.close()
                } else {
                    selectedFileName = it.lastPathSegment ?: "document.txt"
                }

                context.contentResolver.openInputStream(it)?.use { stream ->
                    val reader = BufferedReader(InputStreamReader(stream, "UTF-8"))
                    fileContent = reader.readText()
                }
            } catch (e: Exception) {
                Toast.makeText(context, if (isVietnamese) "Lỗi đọc tệp: ${e.message}" else "Error reading file: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    val primaryBlue = Color(0xFF1976D2)
    val bgLight = Color(0xFFF8F9FA)

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = if (isVietnamese) "Dịch Thuật Đa Năng" else "Universal Translator",
                            fontWeight = FontWeight.Bold,
                            fontSize = 17.sp,
                            color = Color.White
                        )
                        Text(
                            text = "Creator: Hong Quang",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = Color(0xFFFFEB3B)
                        )
                    }
                },
                actions = {
                    Row(
                        modifier = Modifier
                            .padding(end = 8.dp)
                            .clip(RoundedCornerShape(20.dp))
                            .background(Color(0xFF0D47A1))
                            .padding(horizontal = 4.dp, vertical = 2.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "🇻🇳 VI",
                            fontSize = 12.sp,
                            fontWeight = if (isVietnamese) FontWeight.Bold else FontWeight.Normal,
                            color = if (isVietnamese) Color.Yellow else Color.White,
                            modifier = Modifier
                                .clickable { isVietnamese = true }
                                .padding(horizontal = 6.dp, vertical = 4.dp)
                        )
                        Text("|", color = Color.LightGray, fontSize = 12.sp)
                        Text(
                            text = "🇬🇧 EN",
                            fontSize = 12.sp,
                            fontWeight = if (!isVietnamese) FontWeight.Bold else FontWeight.Normal,
                            color = if (!isVietnamese) Color.Yellow else Color.White,
                            modifier = Modifier
                                .clickable { isVietnamese = false }
                                .padding(horizontal = 6.dp, vertical = 4.dp)
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = primaryBlue)
            )
        },
        containerColor = bgLight
    ) { innerPadding ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            TabRow(
                selectedTabIndex = selectedTab,
                containerColor = Color.White,
                contentColor = primaryBlue
            ) {
                Tab(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    text = { Text(if (isVietnamese) "📝 Dịch Văn Bản" else "📝 Text Translation", fontWeight = FontWeight.Bold) }
                )
                Tab(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    text = { Text(if (isVietnamese) "📁 Dịch Tệp Tin" else "📁 File Translation", fontWeight = FontWeight.Bold) }
                )
            }

            // Language Selector Bar (shared)
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(2.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 12.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    LanguageDropdown(
                        selectedCode = sourceLangCode,
                        isSource = true,
                        isVietnamese = isVietnamese,
                        onSelect = { sourceLangCode = it },
                        modifier = Modifier.weight(1f)
                    )

                    IconButton(
                        onClick = {
                            if (sourceLangCode != "auto") {
                                val temp = sourceLangCode
                                sourceLangCode = targetLangCode
                                targetLangCode = temp
                            }
                        }
                    ) {
                        Text("⇄", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = primaryBlue)
                    }

                    LanguageDropdown(
                        selectedCode = targetLangCode,
                        isSource = false,
                        isVietnamese = isVietnamese,
                        onSelect = { targetLangCode = it },
                        modifier = Modifier.weight(1f)
                    )
                }
            }

            if (selectedTab == 0) {
                // TAB 1: TEXT TRANSLATION
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 12.dp)
                        .verticalScroll(rememberScrollState())
                ) {
                    // Input Card
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = Color.White)
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = if (isVietnamese) "Văn bản nguồn" else "Original Text",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                    color = Color.DarkGray
                                )
                                Row {
                                    TextButton(onClick = {
                                        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                                        val clip = clipboard.primaryClip
                                        if (clip != null && clip.itemCount > 0) {
                                            inputText = clip.getItemAt(0).text.toString()
                                        }
                                    }) {
                                        Text(if (isVietnamese) "Dán" else "Paste", fontSize = 12.sp)
                                    }
                                    TextButton(onClick = { inputText = "" }) {
                                        Text(if (isVietnamese) "Xóa" else "Clear", fontSize = 12.sp, color = Color.Red)
                                    }
                                }
                            }

                            OutlinedTextField(
                                value = inputText,
                                onValueChange = { inputText = it },
                                placeholder = { Text(if (isVietnamese) "Nhập hoặc dán văn bản cần dịch..." else "Type or paste text to translate...") },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .heightIn(min = 120.dp),
                                shape = RoundedCornerShape(8.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Button(
                        onClick = {
                            if (inputText.isBlank()) {
                                Toast.makeText(context, if (isVietnamese) "Vui lòng nhập văn bản" else "Please enter text", Toast.LENGTH_SHORT).show()
                                return@Button
                            }
                            isTranslatingText = true
                            outputText = if (isVietnamese) "⏳ Đang dịch văn bản, vui lòng chờ..." else "⏳ Translating, please wait..."
                            coroutineScope.launch {
                                val res = TranslationEngine.translate(inputText, targetLangCode, sourceLangCode)
                                isTranslatingText = false
                                res.onSuccess { outputText = it }
                                res.onFailure {
                                    val err = (if (isVietnamese) "❌ Lỗi dịch: " else "❌ Translation error: ") + (it.message ?: "Network error")
                                    outputText = err
                                    Toast.makeText(context, err, Toast.LENGTH_LONG).show()
                                }
                            }
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(48.dp),
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = primaryBlue),
                        enabled = !isTranslatingText
                    ) {
                        if (isTranslatingText) {
                            CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                        } else {
                            Text(if (isVietnamese) "🚀 DỊCH NGAY" else "🚀 TRANSLATE NOW", fontWeight = FontWeight.Bold)
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    // Output Card
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = Color.White)
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = if (isVietnamese) "Bản dịch kết quả" else "Translation Result",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                    color = Color(0xFF2E7D32)
                                )
                                Row {
                                    TextButton(onClick = {
                                        if (outputText.isNotBlank()) {
                                            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                                            clipboard.setPrimaryClip(ClipData.newPlainText("Translation", outputText))
                                            Toast.makeText(context, if (isVietnamese) "Đã sao chép!" else "Copied to clipboard!", Toast.LENGTH_SHORT).show()
                                        }
                                    }) {
                                        Text(if (isVietnamese) "Sao chép" else "Copy", fontSize = 12.sp)
                                    }
                                    TextButton(onClick = {
                                        if (outputText.isNotBlank()) {
                                            val sendIntent = Intent().apply {
                                                action = Intent.ACTION_SEND
                                                putExtra(Intent.EXTRA_TEXT, outputText)
                                                type = "text/plain"
                                            }
                                            context.startActivity(Intent.createChooser(sendIntent, if (isVietnamese) "Chia sẻ bản dịch" else "Share translation"))
                                        }
                                    }) {
                                        Text(if (isVietnamese) "Chia sẻ" else "Share", fontSize = 12.sp)
                                    }
                                }
                            }

                            OutlinedTextField(
                                value = outputText,
                                onValueChange = {},
                                readOnly = true,
                                placeholder = { Text(if (isVietnamese) "Bản dịch sẽ xuất hiện ở đây..." else "Translation will appear here...") },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .heightIn(min = 120.dp),
                                shape = RoundedCornerShape(8.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(24.dp))
                }
            } else {
                // TAB 2: FILE TRANSLATION
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 12.dp)
                        .verticalScroll(rememberScrollState())
                ) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = Color.White)
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(
                                text = if (isVietnamese) "1. Chọn Tệp Tin Cần Dịch" else "1. Select File to Translate",
                                fontWeight = FontWeight.Bold,
                                fontSize = 15.sp,
                                color = primaryBlue
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = if (isVietnamese) "Hỗ trợ các định dạng: .txt, .srt, .vtt, .csv, .json, .md..." else "Supports formats: .txt, .srt, .vtt, .csv, .json, .md...",
                                fontSize = 12.sp,
                                color = Color.Gray
                            )
                            Spacer(modifier = Modifier.height(12.dp))

                            Button(
                                onClick = { filePickerLauncher.launch("*/*") },
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF42A5F5))
                            ) {
                                Text(if (isVietnamese) "📂 Duyệt Chọn Tệp..." else "📂 Pick File...")
                            }

                            if (selectedFileName.isNotBlank()) {
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = if (isVietnamese) "Đã chọn: $selectedFileName (${fileContent.length} ký tự)" else "Selected: $selectedFileName (${fileContent.length} chars)",
                                    fontWeight = FontWeight.Medium,
                                    fontSize = 13.sp,
                                    color = Color(0xFF1565C0)
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Button(
                        onClick = {
                            if (fileContent.isBlank()) {
                                Toast.makeText(context, if (isVietnamese) "Vui lòng chọn tệp tin trước" else "Please pick a file first", Toast.LENGTH_SHORT).show()
                                return@Button
                            }
                            isTranslatingFile = true
                            translatedFileContent = if (isVietnamese) "⏳ Đang dịch tệp tin, vui lòng chờ..." else "⏳ Translating file, please wait..."
                            coroutineScope.launch {
                                val res = TranslationEngine.translate(fileContent, targetLangCode, sourceLangCode)
                                isTranslatingFile = false
                                res.onSuccess {
                                    translatedFileContent = it
                                    Toast.makeText(context, if (isVietnamese) "Dịch tệp thành công!" else "File translated successfully!", Toast.LENGTH_SHORT).show()
                                }
                                res.onFailure {
                                    val err = (if (isVietnamese) "❌ Lỗi dịch: " else "❌ Translation error: ") + (it.message ?: "Network error")
                                    translatedFileContent = err
                                    Toast.makeText(context, err, Toast.LENGTH_LONG).show()
                                }
                            }
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(48.dp),
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = primaryBlue),
                        enabled = !isTranslatingFile && fileContent.isNotBlank()
                    ) {
                        if (isTranslatingFile) {
                            CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                        } else {
                            Text(if (isVietnamese) "🚀 BẮT ĐẦU DỊCH TỆP" else "🚀 TRANSLATE FILE", fontWeight = FontWeight.Bold)
                        }
                    }

                    if (translatedFileContent.isNotBlank()) {
                        Spacer(modifier = Modifier.height(12.dp))
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(12.dp),
                            colors = CardDefaults.cardColors(containerColor = Color.White)
                        ) {
                            Column(modifier = Modifier.padding(12.dp)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = if (isVietnamese) "Xem trước kết quả dịch" else "Translated Preview",
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 14.sp,
                                        color = Color(0xFF2E7D32)
                                    )
                                    Row {
                                        TextButton(onClick = {
                                            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                                            clipboard.setPrimaryClip(ClipData.newPlainText("File Translation", translatedFileContent))
                                            Toast.makeText(context, if (isVietnamese) "Đã sao chép!" else "Copied!", Toast.LENGTH_SHORT).show()
                                        }) {
                                            Text(if (isVietnamese) "Sao chép" else "Copy", fontSize = 12.sp)
                                        }
                                        TextButton(onClick = {
                                            val sendIntent = Intent().apply {
                                                action = Intent.ACTION_SEND
                                                putExtra(Intent.EXTRA_TEXT, translatedFileContent)
                                                type = "text/plain"
                                            }
                                            context.startActivity(Intent.createChooser(sendIntent, if (isVietnamese) "Chia sẻ tệp đã dịch" else "Share translated file"))
                                        }) {
                                            Text(if (isVietnamese) "Chia sẻ" else "Share", fontSize = 12.sp)
                                        }
                                    }
                                }

                                OutlinedTextField(
                                    value = translatedFileContent,
                                    onValueChange = {},
                                    readOnly = true,
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .heightIn(min = 150.dp, max = 300.dp),
                                    shape = RoundedCornerShape(8.dp)
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(24.dp))
                }
            }
        }
    }
}

@Composable
fun LanguageDropdown(
    selectedCode: String,
    isSource: Boolean,
    isVietnamese: Boolean,
    onSelect: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }
    val languages = TranslationEngine.languages

    val currentName = if (isSource && selectedCode == "auto") {
        if (isVietnamese) "Tự động phát hiện" else "Auto Detect"
    } else {
        val found = languages.find { it.code == selectedCode }
        if (isVietnamese) (found?.nameVi ?: selectedCode) else (found?.nameEn ?: selectedCode)
    }

    Box(modifier = modifier) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(8.dp))
                .background(Color(0xFFF0F4F8))
                .clickable { expanded = true }
                .padding(horizontal = 8.dp, vertical = 6.dp)
        ) {
            Text(
                text = if (isSource) (if (isVietnamese) "Nguồn" else "Source") else (if (isVietnamese) "Đích" else "Target"),
                fontSize = 10.sp,
                color = Color.Gray
            )
            Text(
                text = currentName,
                fontSize = 13.sp,
                fontWeight = FontWeight.Bold,
                color = Color.Black,
                maxLines = 1
            )
        }

        DropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            if (isSource) {
                DropdownMenuItem(
                    text = { Text(if (isVietnamese) "✨ Tự động phát hiện" else "✨ Auto Detect") },
                    onClick = {
                        onSelect("auto")
                        expanded = false
                    }
                )
            }
            languages.forEach { lang ->
                DropdownMenuItem(
                    text = { Text(if (isVietnamese) lang.nameVi else lang.nameEn) },
                    onClick = {
                        onSelect(lang.code)
                        expanded = false
                    }
                )
            }
        }
    }
}
