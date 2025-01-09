import os
import time
from pytube import YouTube
from flask import Flask, render_template, request, send_from_directory, jsonify
from threading import Thread

app = Flask(__name__)
DOWNLOAD_FOLDER = 'download'

# ダウンロードフォルダが存在しない場合に作成
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


# 動画のダウンロード処理
def download_video(url, video_id):
    try:
        yt = YouTube(url)

        # FHD（1080p）が存在する場合はそれを選択
        stream = yt.streams.filter(res="1080p", file_extension="mp4").first()
        if stream is None:
            # FHDがない場合、最高の解像度を選択
            stream = yt.streams.filter(
                file_extension="mp4").get_highest_resolution()

        # ダウンロード
        file_path = os.path.join(DOWNLOAD_FOLDER, f"Download-{video_id}.mp4")
        stream.download(output_path=DOWNLOAD_FOLDER,
                        filename=f"Download-{video_id}.mp4")

        # 10分後にファイルを削除
        time.sleep(600)  # 600秒 = 10分
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        print(f"Error downloading video {video_id}: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    try:
        # 動画IDを取得
        video_id = YouTube(url).video_id

        # 動画を非同期でダウンロード
        thread = Thread(target=download_video, args=(url, video_id))
        thread.start()

        return jsonify({
            "status": "success",
            "message": "ダウンロード中です",
            "video_id": video_id
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"エラー: {str(e)}"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
