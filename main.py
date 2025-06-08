import flet as ft
from flet import Page
from flet_audio import Audio
from dotenv import load_dotenv
import google.generativeai as genai
import time
import socket
import subprocess
import uuid
import base64
import requests
import os

# 環境変数の読み込みとAPIキー設定
if load_dotenv(verbose=True):
    print(".env ファイルを読み込みました。")
else:
    print(".env ファイルが見つかりませんでした。")

google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    raise RuntimeError("GOOGLE_API_KEYが.envファイルに設定されていません。")
genai.configure(api_key=google_api_key)

# VOICEVOX 設定
ENGINE_URL = "http://127.0.0.1:50021"
current_speaker_id = 100
# PC内のVOECEVOXの絶対パスを入力
voicevox_exe_path = os.getenv('VOICEVOX_EXE_PATH')
if not voicevox_exe_path:
    raise RuntimeError("VOICEVOX_EXE_PATHが.envファイルに設定されていません。")

def is_port_open(host='127.0.0.1', port=50021):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
            return True
        except:
            return False

def launch_voicevox(exe_path):
    subprocess.Popen([exe_path], shell=False)

def wait_for_port(host='127.0.0.1', port=50021, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(host, port):
            return True
        time.sleep(1)
    return False

if not is_port_open():
    print("VOICEVOXを起動します...")
    launch_voicevox(voicevox_exe_path)
    if not wait_for_port():
        raise RuntimeError("VOICEVOX APIポートに接続できませんでした。")

def synthesize_voicevox(text: str, output_file: str):
    # グローバル current_speaker_id を参照
    res1 = requests.post(
        f"{ENGINE_URL}/audio_query",
        params={"speaker": current_speaker_id, "text": text}
    )
    res1.raise_for_status()
    audio_query = res1.json()

    res2 = requests.post(
        f"{ENGINE_URL}/synthesis",
        params={"speaker": current_speaker_id},
        json=audio_query
    )
    res2.raise_for_status()

    with open(output_file, "wb") as f:
        f.write(res2.content)

# メインアプリ
def main(page: Page):
    global current_speaker_id
    page.title = "Gemini / VOICEVOX (ずんだもん・四国めたん・春日部つむぎ・黒沢冴白)"
    page.vertical_alignment = ft.MainAxisAlignment.END

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    )
    chat = model.start_chat(history=[])

    chat_log = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    user_input = ft.TextField(hint_text="メッセージを入力", expand=True)
    send_button = ft.ElevatedButton("送信")
    delete_button = ft.ElevatedButton("すべての .wav ファイルを削除")
    audio_control = Audio(src="about:blank", autoplay=True)

    async def send_message(e):
        if user_input.value.strip() == "":
            return

        user_message = user_input.value
        user_input.value = ""

        chat_log.controls.append(
            ft.Container(
                content=ft.Text(user_message),
                padding=10,
                bgcolor=ft.Colors.BLUE_100,
                border_radius=10,
                alignment=ft.alignment.center_right
            )
        )
        page.update()

        thinking_indicator = ft.Container(
            content=ft.ProgressRing(width=20, height=20, stroke_width=2),
            padding=10,
            alignment=ft.alignment.center_left
        )
        chat_log.controls.append(thinking_indicator)
        page.update()

        try:
            response = await chat.send_message_async(user_message)
            gemini_response_text = response.text
        except Exception as ex:
            gemini_response_text = f"エラー: {ex}"
        finally:
            chat_log.controls.remove(thinking_indicator)
            page.update()

        chat_log.controls.append(
            ft.Container(
                content=ft.Text(f"Gemini: {gemini_response_text}"),
                padding=10,
                bgcolor=ft.Colors.GREY_200,
                border_radius=10,
                alignment=ft.alignment.center_left
            )
        )
        page.update()

        try:
            voice_file = f"voice_{uuid.uuid4().hex}.wav"
            synthesize_voicevox(gemini_response_text, voice_file)

            # 音声ファイルをBase64エンコードして読み込む
            with open(voice_file, "rb") as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            audio_control.src = f"data:audio/wav;base64,{audio_base64}"
            audio_control.autoplay = True
            audio_control.update()
            page.update()
        except Exception as e:
            chat_log.controls.append(
                ft.Text(f"VOICEVOX エラー: {e}", color=ft.Colors.RED)
            )
            page.update()

    def on_select_speaker(e: ft.ControlEvent):
        global current_speaker_id
        current_speaker_id = int(e.control.value)
        page.snack_bar = ft.SnackBar(
            ft.Text(f"話者を切り替えました: ID {current_speaker_id}")
        )
        page.snack_bar.open = True
        page.update()

    speaker_dropdown = ft.Dropdown(
        label="キャラ変更",
        options=[
            ft.dropdown.Option("1", "ずんだもん"),
            ft.dropdown.Option("2", "四国めたん"),
            ft.dropdown.Option("8", "春日部つむぎ"),
            ft.dropdown.Option("100", "黒沢冴白"),
        ],
        value="100",  # デフォルト黒沢冴白
        on_change=on_select_speaker,
        width=150
    )

    def delete_wav_files(e):
        for filename in os.listdir("."):
            if filename.endswith(".wav") and filename.startswith("voice_"):
                try:
                    os.remove(filename)
                except Exception as ex:
                    print(f"削除エラー: {filename} - {ex}")

    send_button.on_click = send_message
    user_input.on_submit = send_message
    delete_button.on_click = delete_wav_files

    page.add(
        speaker_dropdown,
        chat_log,
        ft.Row([user_input, send_button]),
        delete_button,
        audio_control
    )

#ft.app(target=main)  # ローカル用
ft.app(target=main, view=ft.WEB_BROWSER)  #Webブラウザ用