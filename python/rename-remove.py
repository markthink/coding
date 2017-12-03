# -*- coding: utf-8 -*-

import os


def mdfilesRemove(path):
    current_files = os.listdir(path)
    all_files = []
    for file_name in current_files:
        full_file_name = os.path.join(path, file_name)
        if (os.path.splitext(full_file_name)[1] == '.md' and os.path.splitext(full_file_name)[0].find('-remove') != -1):
            all_files.append(full_file_name)

        if os.path.isdir(full_file_name):
            next_level_files = mdfilesRemove(full_file_name)
            all_files.extend(next_level_files)
    return all_files


if __name__ == '__main__':

    baseurl = "/Users/dxwsker/works/lab/kubernetes.github.io/docs"

    MDfiles = mdfilesRemove(baseurl)

    # file = open("mdfiles-remove.txt", "w+", encoding='utf-8')

    for i in range(0, len(MDfiles)):
        filename = MDfiles[i].split('-remove')[0]
        filenameMd = filename +".md"

        # print(MDfiles[i] + "\n" + filename)
        os.rename(filenameMd, filename+"-bak.md")
        os.rename(MDfiles[i], filenameMd)

        # filename = MDfiles[i].split('-bak')[0]
        # print(MDfiles[i]+"\n"+filename)
        # os.rename(MDfiles[i], filename)

    # 重命名测试
    # filename = "/Users/dxwsker/works/lab/kubernetes.github.io/docs/admin/kubeadm"
    # os.rename(filename+".md", filename+"-bak.md")
    # os.rename(filename + "-remove.md", filename + ".md")
