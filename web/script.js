// アダプタのリストを読み込み、ドロップダウンを更新する関数
function loadInterfaces() {
    const select = document.getElementById('adapter-select');
    const currentValue = select.value; // 現在選択されている値を保持

    // 既存のオプションをクリア（「-- アダプタを選択 --」の最初の1つは残す）
    while (select.options.length > 1) {
        select.remove(1);
    }

    // Pythonのget_interfaces_with_status関数を呼び出して最新の情報を取得
    pywebview.api.get_interfaces_with_status().then(function(interfacesJson) {
        const interfaces = JSON.parse(interfacesJson);
        
        // 取得した情報でドロップダウンを再生成
        interfaces.forEach(function(item) {
            const option = document.createElement('option');
            option.value = item.name;
            option.textContent = `${item.name} (IPv6: ${item.status})`;
            select.appendChild(option);
        });

        // 可能であれば、以前選択されていた値を再度選択状態にする
        select.value = currentValue;
    });
}


// pywebviewのAPIが利用可能になったら初回読み込みを実行
window.addEventListener('pywebviewready', function() {
    loadInterfaces();
});


// IPv6の状態を変更するメインの関数
function setIPv6State(state) {
    const select = document.getElementById('adapter-select');
    const adapterName = select.value;
    const statusDiv = document.getElementById('status');
    
    if (!adapterName) {
        statusDiv.textContent = 'アダプタを選択してください。';
        statusDiv.style.borderLeftColor = '#dc3545';
        return;
    }
    
    statusDiv.textContent = '処理中...';

    // Pythonのset_ipv6_state関数を呼び出す
    pywebview.api.set_ipv6_state(adapterName, state).then(function(responseJson) {
        const response = JSON.parse(responseJson);
        statusDiv.textContent = response.message;
        statusDiv.style.borderLeftColor = response.success ? '#005a9e' : '#dc3545';

        // 成功した場合、ページ全体をリロードする代わりに、リストだけを更新する
        if (response.success) {
            // 1.5秒待ってからリストを更新（ユーザーがメッセージを読む時間）
            setTimeout(loadInterfaces, 1500);
        }
    });
}

// ボタンにクリックイベントを割り当て
document.getElementById('enable-btn').addEventListener('click', function() {
    setIPv6State('enable');
});

document.getElementById('disable-btn').addEventListener('click', function() {
    setIPv6State('disable');
});
