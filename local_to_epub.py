import os
import subprocess
import shutil
import tempfile

# --- 配置 ---
SOURCE_DIR = "zh-cn"  # 假设你在根目录运行，中文内容在此文件夹
OUTPUT_NAME = "Software_Engineering_at_Google_ZH.epub"
TITLE = "Google 软件工程 (中文版)"
AUTHOR = "Titus Winters, Tom Manshreck, Hyrum Wright"

def generate_epub():
    # 1. 检查目录是否存在
    if not os.path.exists(SOURCE_DIR):
        print(f"错误：找不到目录 '{SOURCE_DIR}'。请确保脚本放在项目根目录。")
        return

    # 2. 创建临时目录并收集所有图片到统一位置
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建临时的统一图片目录
        temp_images_dir = os.path.join(temp_dir, 'images')
        os.makedirs(temp_images_dir, exist_ok=True)
        
        # 遍历所有章节目录，收集图片
        for root, dirs, files in os.walk(SOURCE_DIR):
            if 'images' in dirs:
                chapter_images_dir = os.path.join(root, 'images')
                for img_file in os.listdir(chapter_images_dir):
                    src_path = os.path.join(chapter_images_dir, img_file)
                    dst_path = os.path.join(temp_images_dir, img_file)
                    # 如果文件名冲突，使用更具体的名称
                    if os.path.exists(dst_path):
                        chapter_name = os.path.basename(root)
                        name, ext = os.path.splitext(img_file)
                        dst_path = os.path.join(temp_images_dir, f"{chapter_name}_{name}{ext}")
                    shutil.copy2(src_path, dst_path)

        # 3. 获取并排序所有 Markdown 文件
        md_files = []
        for root, dirs, files in os.walk(SOURCE_DIR):
            for f in files:
                if f.endswith(".md") and "README" not in f.upper():
                    # 记录完整路径
                    md_files.append(os.path.join(root, f))
        
        # 核心步骤：排序。根据文件名开头的数字排序，确保章节不乱
        md_files.sort(key=lambda x: os.path.basename(x))

        if not md_files:
            print("没有找到任何 Markdown 文件。")
            return

        print(f"共检测到 {len(md_files)} 个章节，正在合并生成...")

        # 4. 构建 Pandoc 命令
        # 将临时目录和源目录添加到资源路径
        pandoc_cmd = [
            "pandoc",
            "-f", "markdown-yaml_metadata_block",  # 明确指定输入格式为 markdown 并禁用 YAML 元数据块解析
            *md_files,
            "-o", OUTPUT_NAME,
            "--toc",                   # 生成目录
            "--toc-depth=2",           # 目录深度
            "--metadata", f"title={TITLE}",
            "--metadata", f"author={AUTHOR}",
            "--resource-path", f".:{temp_dir}", # 包含临时目录作为资源路径
        ]

        try:
            subprocess.run(pandoc_cmd, check=True)
            print("-" * 30)
            print(f"恭喜！生成成功：\n{os.path.abspath(OUTPUT_NAME)}")
            print("-" * 30)
        except subprocess.CalledProcessError as e:
            print(f"转换过程中出错：{e}")
        except FileNotFoundError:
            print("错误：系统未找到 Pandoc，请先安装 Pandoc。")

if __name__ == "__main__":
    generate_epub()