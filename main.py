import webview
import sys
import ctypes
import os

# 分離したロジック担当のモジュールから必要な関数をインポート
from ipv6_handler import is_admin, get_interfaces_with_status, set_ipv6_state

class Api:
    """
    JavaScriptフロントエンドに公開されるAPIクラスです。
    実際の処理はipv6_handlerモジュールに委譲します。
    """
    def get_interfaces_with_status(self):
        """UIからの要求に応じて、アダプタ一覧と状態を取得する関数を呼び出します。"""
        return get_interfaces_with_status()

    def set_ipv6_state(self, interface_name, state):
        """UIからの要求に応じて、IPv6状態変更関数を呼び出します。"""
        return set_ipv6_state(interface_name, state)

if __name__ == '__main__':
    # 実行時に管理者権限を確認します
    if is_admin():
        # 管理者権限がある場合、webviewアプリケーションを作成して開始します
        api = Api()
        
        # HTMLファイルのパスをwebディレクトリ内に変更
        html_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'web', 'index.html')

        window = webview.create_window(
            'IPv6 設定ツール',
            html_file, # webディレクトリ内のHTMLを読み込む
            js_api=api,
            width=550,
            height=420,
            resizable=False,
            text_select=True
        )
        webview.start()
    else:
        # 管理者権限がない場合、権限を昇格させてスクリプトを再起動します
        # この時点で現在のプロセスは終了するため、元のターミナルは残りません。
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)
