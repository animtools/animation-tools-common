import re

def format_filename(template:str, title:str, episode:int, scene:int, cut:int):
    """
    # 使用例
    template = "{TITLE}_S{SCENE}_C{CUT}.mov"
    result = format_filename(template, "ProjectX", 1, 23)
    print(result)  # 出力: ProjectX_S001_C0023.mov
    """
    # 予約語を実際の値に置換
    filename = template.replace("{TITLE}", title)
    filename = filename.replace("{EPISODE}", f"{int(episode):02d}")
    filename = filename.replace("{SCENE}", f"{int(scene):03d}")
    filename = filename.replace("{CUT}", f"{int(cut):04d}")
    # 不正な文字を除去（オプション）
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    return filename

def parse_filename(template:str, filename:str):
    """
    # 使用例
    template = "{TITLE}_S{SCENE}_C{CUT}.mov"
    filename = "ProjectX_S001_C0023.mov"

    result = parse_filename(template, filename)
    print(result)
    """
    # テンプレートを正規表現パターンに変換
    pattern = re.escape(template)
    pattern = pattern.replace(r'\{TITLE\}', r'(?P<TITLE>[^_]+)')
    pattern = pattern.replace(r'\{EPISODE\}', r'(?P<EPISODE>\d+)')
    pattern = pattern.replace(r'\{SCENE\}', r'(?P<SCENE>\d+)')
    pattern = pattern.replace(r'\{CUT\}', r'(?P<CUT>\d+)')
    
    # 正規表現でファイル名をマッチング
    match = re.match(pattern, filename)
    
    if match:
        # マッチした場合、各グループの値を取得
        result = match.groupdict()
        
        # シーン番号とカット番号を整数に変換
        if 'EPISODE' in result:
            result['EPISODE'] = int(result['EPISODE'])
        if 'SCENE' in result:
            result['SCENE'] = int(result['SCENE'])
        if 'CUT' in result:
            result['CUT'] = int(result['CUT'])

        return result
    else:
        # マッチしない場合はNoneを返す
        return None