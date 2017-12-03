# -*- coding: utf-8 -*-

import os,subprocess,codecs;

# 定义过滤数据规则
FH_SPACE = FHS = ((u"　", u" "),)
FH_NUM = FHN = (
    (u"０", u"0"), (u"１", u"1"), (u"２", u"2"), (u"３", u"3"), (u"４", u"4"),
    (u"５", u"5"), (u"６", u"6"), (u"７", u"7"), (u"８", u"8"), (u"９", u"9"),
)
FH_ALPHA = FHA = (
    (u"ａ", u"a"), (u"ｂ", u"b"), (u"ｃ", u"c"), (u"ｄ", u"d"), (u"ｅ", u"e"),
    (u"ｆ", u"f"), (u"ｇ", u"g"), (u"ｈ", u"h"), (u"ｉ", u"i"), (u"ｊ", u"j"),
    (u"ｋ", u"k"), (u"ｌ", u"l"), (u"ｍ", u"m"), (u"ｎ", u"n"), (u"ｏ", u"o"),
    (u"ｐ", u"p"), (u"ｑ", u"q"), (u"ｒ", u"r"), (u"ｓ", u"s"), (u"ｔ", u"t"),
    (u"ｕ", u"u"), (u"ｖ", u"v"), (u"ｗ", u"w"), (u"ｘ", u"x"), (u"ｙ", u"y"), (u"ｚ", u"z"),
    (u"Ａ", u"A"), (u"Ｂ", u"B"), (u"Ｃ", u"C"), (u"Ｄ", u"D"), (u"Ｅ", u"E"),
    (u"Ｆ", u"F"), (u"Ｇ", u"G"), (u"Ｈ", u"H"), (u"Ｉ", u"I"), (u"Ｊ", u"J"),
    (u"Ｋ", u"K"), (u"Ｌ", u"L"), (u"Ｍ", u"M"), (u"Ｎ", u"N"), (u"Ｏ", u"O"),
    (u"Ｐ", u"P"), (u"Ｑ", u"Q"), (u"Ｒ", u"R"), (u"Ｓ", u"S"), (u"Ｔ", u"T"),
    (u"Ｕ", u"U"), (u"Ｖ", u"V"), (u"Ｗ", u"W"), (u"Ｘ", u"X"), (u"Ｙ", u"Y"), (u"Ｚ", u"Z"),
)
FH_PUNCTUATION = FHP = (
    (u"．", u"."), (u"，", u","), (u"！", u"!"), (u"？", u"?"), (u"”", u'"'),
    (u"’", u"'"), (u"‘", u"`"), (u"＠", u"@"), (u"＿", u"_"), (u"：", u":"),
    (u"；", u";"), (u"＃", u"#"), (u"＄", u"$"), (u"％", u"%"), (u"＆", u"&"),
    (u"（", u"("), (u"）", u")"), (u"‐", u"-"), (u"＝", u"="), (u"＊", u"*"),
    (u"＋", u"+"), (u"－", u"-"), (u"／", u"/"), (u"＜", u"<"), (u"＞", u">"),
    (u"［", u"["), (u"￥", u"\\"), (u"］", u"]"), (u"＾", u"^"), (u"｛", u"{"),
    (u"｜", u"|"), (u"｝", u"}"), (u"～", u"~"),
)
FH_ASCII = HAC = lambda: ((fr, to) for m in (FH_ALPHA, FH_NUM, FH_PUNCTUATION) for fr, to in m)

HF_SPACE = HFS = ((u" ", u"　"),)
HF_NUM = HFN = lambda: ((h, z) for z, h in FH_NUM)
HF_ALPHA = HFA = lambda: ((h, z) for z, h in FH_ALPHA)
HF_PUNCTUATION = HFP = lambda: ((h, z) for z, h in FH_PUNCTUATION)
HF_ASCII = ZAC = lambda: ((h, z) for z, h in FH_ASCII())


# 定义翻译函数
class KubernetesDoc:

    # 首次全量翻译/增量翻译更新一下路径地址
    baseurl = "/Users/dxwsker/works/lab/kubernetes.github.io/docs"

    # 获取所有需要翻译的 MD 文件列表
    def mdfiles(self,path):
        current_files = os.listdir(path)
        all_files = []
        for file_name in current_files:
            full_file_name = os.path.join(path, file_name)
            if (os.path.splitext(full_file_name)[1] == '.md' and os.path.dirname(full_file_name).find("node_modules") == -1):
                # print(os.path.dirname(full_file_name))
                all_files.append(full_file_name)

            if os.path.isdir(full_file_name):
                next_level_files = self.mdfiles(full_file_name)
                all_files.extend(next_level_files)
        return all_files


    # convert(text, FH_ASCII, {u"【": u"[", u"】": u"]", u",": u"，", u".": u"。", u"?": u"？", u"!": u"！"}, spit="，。？！“”")
    def convert(self, text, *maps, **ops):
        """ 全角/半角转换
        args:
            text: unicode string need to convert
            maps: conversion maps
            skip: skip out of character. In a tuple or string
            return: converted unicode string
        """
        if "skip" in ops:
            skip = ops["skip"]
            if isinstance(skip, str):
                skip = tuple(skip)

            def replace(text, fr, to):
                return text if fr in skip else text.replace(fr, to)
        else:
            def replace(text, fr, to):
                return text.replace(fr, to)

        for m in maps:
            if callable(m):
                m = m()
            elif isinstance(m, dict):
                m = m.items()
            for fr, to in m:
                text = replace(text, fr, to)
        return text


if __name__ == '__main__':

    k8s = KubernetesDoc()

    MDfiles = k8s.mdfiles(k8s.baseurl)

    # file = open("mdfiles.txt", "w+", encoding='utf-8')
    # for i in range(0, len(MDfiles)):
    #     file.write(MDfiles[i]+"\n")

    file = open("mdfiles.txt", "r", encoding='utf-8')
    MDfiles = file.readlines()
    file.close()

    # MDfiles=['/Users/dxwsker/works/k8s.io/dog.txt','/Users/dxwsker/works/k8s.io/cat.txt']

    for i in range(0, len(MDfiles)):
        print("begin-trans:",i, MDfiles[i])
        # filename = os.path.splitext(MDfiles[i])[0] + "-new.md"
        filename = os.path.splitext(MDfiles[i])[0].strip("\n")

        # trans_cmd = "trans -b :zh-CN -i " + MDfiles[i] + " -o "+ filename
        trans_cmd = "trans -b :zh-CN -i " + filename + ".md -o "+filename+"-remove.md"
        subprocess.run(trans_cmd,shell=True)

        # 字符全角转半角预处理
        file = open(filename+"-remove.md", "r", encoding='utf-8')
        text = file.read()
        file.close()
        output = k8s.convert(text, FH_ASCII,
                         {u"【": u"[", u"】": u"]", u",": u"，", u".": u"。", u"?": u"？", u"!": u"！", u"/ ": u"/",
                          u" /": u"/"}, spit="，？！“”")

        file = open(filename+"-remove.md", "w+", encoding='utf-8')
        file.truncate()
        file.write(output)
        file.close()

        # 重命名文件
        os.rename(filename+".md", filename + "-bak.md")
        os.rename(filename+"-remove.md", filename+".md")

        print("end-trans:", i, MDfiles[i])
    print("process finish")

# sed -i 's/。/./g' `grep -rl '。' --include="*.md" ./`

# sed -i 's/$ /$/g' `grep -rl '$ ' --include="*.md" ./`

# sed -i 's/！\[/!\[/g' `grep -rl '！\[' --include="*.md" ./`
