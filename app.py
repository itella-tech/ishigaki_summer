import requests
import streamlit as st
import json
import os
import uuid

def get_workflows(api_key):
    url = 'https://api.dify.ai/v1/workflows'
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        workflows = response.json()["data"]
        return {workflow["name"]: workflow["id"] for workflow in workflows}
    else:
        st.error(f"ワークフローの取得に失敗しました: {response.status_code}")
        return {}

def execute_workflow_streaming(api_key, inputs, user_id):
    url = 'https://api.dify.ai/v1/workflows/run'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'inputs': inputs,
        'response_mode': 'blocking',
        'user': user_id
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return {
            'workflow_run_id': result.get('workflow_run_id'),
            'task_id': result.get('task_id'),
            'status': result['data'].get('status'),
            'outputs': result['data'].get('outputs'),
            'error': result['data'].get('error'),
            'elapsed_time': result['data'].get('elapsed_time'),
            'total_tokens': result['data'].get('total_tokens'),
            'total_steps': result['data'].get('total_steps'),
            'created_at': result['data'].get('created_at'),
            'finished_at': result['data'].get('finished_at')
        }
    else:
        st.error(f"ワークフローの実行に失敗しました: {response.status_code}")
        return None

# Streamlitアプリケーションの設定
st.title('夏休みデジタル教室')

api_key = os.environ.get('DIFY_API_KEY')
if not api_key:
    api_key = 'app-xxx'  # デフォルトのAPI key

# ユーザーIDの生成（セッションごとに一意）
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# タブの作成
tab1, tab2 = st.tabs(["テキスト生成", "画像生成"])

with tab1:
    st.header("テキスト生成")
    # 入力フィールドの追加
    query = st.text_input('プロンプト')

    if st.button('生成する'):
        inputs = {
            'query': query,
            'type': 'image'
        }
        with st.spinner("ワークフローを実行中..."):
            response = execute_workflow_streaming(api_key, inputs, st.session_state.user_id)
            if response and 'outputs' in response:
                st.write("ワークフロー実行結果:")
                st.write(response['outputs']['text'])

with tab2:
    st.header("画像生成")
    image_prompt = st.text_input('画像生成プロンプト')
    
    if st.button('生成する'):
        inputs = {
            'query': image_prompt,
            'type': 'image'
        }
        with st.spinner("画像を生成中..."):
            response = execute_workflow_streaming(api_key, inputs, st.session_state.user_id)
            if response and 'outputs' in response:
                st.write("画像生成結果:")
                print(response['outputs'])
                if 'json' in response['outputs']:
                    image_data = response['outputs']['json'][0]
                    if image_data['type'] == 'image' and 'url' in image_data:
                        st.image(image_data['url'])
                    else:
                        st.write("画像データが正しい形式ではありません。")
                else:
                    st.write("画像データが見つかりません。")
