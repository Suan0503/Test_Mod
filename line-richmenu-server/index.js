require('dotenv').config();

const express = require('express');
const cors = require('cors');
const multer = require('multer');
const axios = require('axios');

const app = express();
const port = process.env.PORT || 3000;

// CORS: 允許前端（例如 Vite / React dev server）呼叫本 API
app.use(cors());

// 不解析 multipart，由 multer 處理

// multer 設定為純記憶體，不可寫入磁碟
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024 // 最多 10MB
  }
});

/**
 * 呼叫 LINE Messaging API 更新 Rich Menu 圖片
 * @param {string} richMenuId
 * @param {Buffer} imageBuffer
 * @param {string} mimeType
 * @returns {Promise<void>}
 */
async function uploadRichMenuImageToLine(richMenuId, imageBuffer, mimeType) {
  const accessToken = process.env.LINE_CHANNEL_ACCESS_TOKEN;
  if (!accessToken) {
    throw new Error('LINE_CHANNEL_ACCESS_TOKEN is not set in environment');
  }

  const url = `https://api.line.me/v2/bot/richmenu/${encodeURIComponent(richMenuId)}/content`;

  await axios.post(url, imageBuffer, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': mimeType,
      'Content-Length': imageBuffer.length
    },
    // 避免過長等待，給一個合理 timeout
    timeout: 15000
  });
}

// POST /api/richmenu/upload-image
app.post(
  '/api/richmenu/upload-image',
  upload.single('image'),
  async (req, res) => {
    try {
      const richMenuId = (req.body.richMenuId || '').trim();
      const file = req.file;

      if (!richMenuId || !file) {
        return res.status(400).json({
          success: false,
          message: 'richMenuId 與 image 檔案為必填'
        });
      }

      if (!file.mimetype.startsWith('image/')) {
        return res.status(400).json({
          success: false,
          message: '上傳檔案必須為圖片格式'
        });
      }

      await uploadRichMenuImageToLine(richMenuId, file.buffer, file.mimetype);

      return res.json({ success: true });
    } catch (err) {
      console.error('[LINE RichMenu Upload] error:', err.response?.data || err.message || err);

      const status = err.response?.status || 500;
      const messageFromLine = err.response?.data?.message || err.response?.data?.error || err.message || 'LINE API error';

      return res.status(status).json({
        success: false,
        message: messageFromLine
      });
    }
  }
);

app.get('/health', (req, res) => {
  res.json({ ok: true, env: 'line-richmenu-server' });
});

app.listen(port, () => {
  console.log(`LINE RichMenu server listening on port ${port}`);
});
