import subprocess
import psutil
import json
import ctypes
import socket

def is_admin():
    """
    スクリプトが管理者権限で実行されているかを確認します。
    管理者権限の場合はTrue、そうでない場合はFalseを返します。
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_interfaces_with_status():
    """
    物理的なイーサネットインターフェースの一覧と、それぞれのIPv6の状態を取得します。
    """
    interfaces_with_status = []
    all_interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    
    for name, addrs in all_interfaces.items():
        if name not in stats or not stats[name].isup:
            continue
            
        has_mac_address = any(addr.family == psutil.AF_LINK for addr in addrs)
        if not has_mac_address:
            continue

        ipv6_enabled = any(addr.family == socket.AF_INET6 for addr in addrs)
        
        status = {
            "name": name,
            "status": "有効" if ipv6_enabled else "無効"
        }
        interfaces_with_status.append(status)
            
    return json.dumps(interfaces_with_status)

def set_ipv6_state(interface_name, state):
    """
    指定されたネットワークインターフェースのIPv6をPowerShellを使用して有効または無効にします。
    netshよりもUnicode文字の扱いに優れています。
    """
    if not interface_name:
        return json.dumps({
            "success": False,
            "message": "ネットワークアダプタが選択されていません。"
        })

    # PowerShellコマンドを構築します。$true / $false はPowerShellの真偽値です。
    ps_state = "$true" if state == "enable" else "$false"
    
    # ComponentID 'ms_tcpip6' は「インターネット プロトコル バージョン 6 (TCP/IPv6)」を指す内部名です。
    # シングルクォートでインターフェース名を囲むことで、特殊文字を安全に扱います。
    command = [
        "powershell",
        "-ExecutionPolicy", "Bypass",  # 実行ポリシーを一時的に回避します
        "-Command",
        f"Set-NetAdapterBinding -Name '{interface_name}' -ComponentID ms_tcpip6 -Enabled {ps_state}"
    ]
    
    try:
        # PowerShellコマンドを実行します
        result = subprocess.run(
            command,
            check=True, 
            capture_output=True, 
            text=True, # Unicodeを正しく扱うために重要です
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        message = f"「{interface_name}」のIPv6を{'有効' if state == 'enable' else '無効'}にしました。\n\n処理は正常に完了しました。"
        
        return json.dumps({"success": True, "message": message})

    except subprocess.CalledProcessError as e:
        # コマンド実行に失敗した場合、詳細なデバッグ情報を生成します。
        error_details = (
            f"コマンドの実行に失敗しました。\n\n"
            f"--- デバッグ情報 ---\n"
            f"実行コマンド: {' '.join(command)}\n"
            f"終了コード: {e.returncode}\n"
            f"PowerShellからのエラー:\n{e.stderr.strip() if e.stderr else '（なし）'}\n"
            f"--------------------"
        )
        return json.dumps({"success": False, "message": error_details})
    except FileNotFoundError:
        return json.dumps({"success": False, "message": "エラー: PowerShellが見つかりませんでした。このツールはPowerShellがインストールされているWindows環境で実行する必要があります。"})
    except Exception as e:
        return json.dumps({"success": False, "message": f"予期せぬエラー: {e}"})
