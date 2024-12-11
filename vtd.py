import os
import argparse
from prompt_toolkit.shortcuts import checkboxlist_dialog

def list_tree(path, prefix="", root_path=None):
    if root_path is None:
        root_path = path
    tree = []
    entries = sorted(os.listdir(path))
    for i, entry in enumerate(entries):
        # full_pathを絶対パス化
        full_path = os.path.abspath(os.path.join(path, entry))
        relative_path = os.path.relpath(full_path, start=root_path)
        connector = "├── " if i < len(entries) - 1 else "└── "
        line = f"{prefix}{connector}{entry}"
        tree.append((line, full_path, relative_path))
        if os.path.isdir(full_path):
            subtree = list_tree(full_path, prefix + ("│   " if i < len(entries) - 1 else "    "), root_path)
            tree.extend(subtree)
    return tree

def select_files_with_prompt(tree):
    # GUI表示部分は修正不要とのことなのでabsoluteなままでも可
    # 改善はひとまず後回し
    file_choices = [(full_path, full_path) for (_, full_path, _) in tree if os.path.isfile(full_path)]
    result = checkboxlist_dialog(
        title="File Selector",
        text="Select files:",
        values=file_choices,
    ).run()
    return result if result else []

def main():
    parser = argparse.ArgumentParser(description="VTD - View Tree Detail")
    parser.add_argument("-p", "--path", type=str, default=os.getcwd(), help="Path to the root directory")
    parser.add_argument("-o", "--output", type=str, help="Path to output the results")
    args = parser.parse_args()

    # 入力パスを絶対パスに変換
    path = os.path.abspath(args.path)
    if not os.path.exists(path):
        print(f"Error: The path {path} does not exist.")
        return

    tree = list_tree(path, root_path=path)
    selected_files = select_files_with_prompt(tree)

    contents = {}
    for file_path in selected_files:
        # selected_filesにはfull_path(絶対パス)が返るはずなので、このままopenできる
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                contents[file_path] = f.read()

    response = "File Tree\n" + "\n".join(line for line, _, _ in tree) + "\n"
    for filename, content in contents.items():
        # 出力時だけはroot_path基準で相対パス表示したい場合
        rel_filename = os.path.relpath(filename, start=path)
        response += f"\n```{rel_filename}\n{content}\n```"

    if args.output:
        output_path = os.path.join(args.output, "vtd_result.txt")
        try:
            with open(output_path, "w", encoding='utf-8') as output_file:
                output_file.write(response)
            print(f"Output written to {output_path}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
    else:
        print(response)

if __name__ == "__main__":
    main()
