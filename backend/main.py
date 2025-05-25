import webview
from api_mvp import SPMAnalyzerMVP

if __name__ == '__main__':
    api = SPMAnalyzerMVP()
    
    window = webview.create_window(
        title='SPM 分析器 V2 (MVP)',
        url='http://localhost:5173',
        js_api=api,
        width=1400,
        height=900
    )
    
    webview.start(debug=True)