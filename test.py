import React, { useState, useEffect, useRef } from "react";
import { saveAs } from "file-saver";

// 한글 폰트 불러오기 (index.html에 추가)
// <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR&display=swap" rel="stylesheet">

export default function StickerMaker() {
  const [emoji, setEmoji] = useState("😀");
  const [label, setLabel] = useState("스티커");
  const canvasRef = useRef(null);

  // 캔버스에 즉시 반영
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    // 캔버스 초기화
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 배경
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 이모지
    ctx.font = "64px Noto Sans KR"; // 한글 지원 폰트
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(emoji, canvas.width / 2, canvas.height / 2 - 20);

    // 텍스트
    ctx.font = "24px Noto Sans KR";
    ctx.fillStyle = "black";
    ctx.fillText(label, canvas.width / 2, canvas.height / 2 + 40);
  }, [emoji, label]); // emoji나 label 바뀌면 자동 렌더링

  const downloadSticker = () => {
    const canvas = canvasRef.current;
    canvas.toBlob((blob) => {
      saveAs(blob, "sticker.png");
    });
  };

  return (
    <div className="flex gap-4">
      <div className="flex flex-col gap-2">
        <input
          type="text"
          value={emoji}
          onChange={(e) => setEmoji(e.target.value)}
          placeholder="이모지 입력"
          className="border p-2"
        />
        <input
          type="text"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          placeholder="텍스트 입력"
          className="border p-2"
        />
        <button onClick={downloadSticker} className="bg-blue-500 text-white p-2 rounded">
          스티커 다운로드
        </button>
      </div>

      <canvas ref={canvasRef} width={200} height={200} className="border" />
    </div>
  );
}
