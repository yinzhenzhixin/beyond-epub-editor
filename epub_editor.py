import re
import sys
import warnings
import argparse
from ebooklib import epub
from bs4 import BeautifulSoup
from tqdm import tqdm
from bs4.builder import XMLParsedAsHTMLWarning

# 忽略XML解析警告
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# 中文和英文标点
PUNCTUATION = "，。！？；：、“”‘’（）《》【】…—"
PUNCTUATION += r"\.,!?;:'\"\)\(\]\[\-"

def tighten_text(text):
    """
    删除非标点符号字符后的所有空白，并压缩段内多余空格
    """
    # 删除非标点后的空白
    pattern = fr"([^\{PUNCTUATION}])\s+"
    text = re.sub(pattern, r"\1", text)
    # 删除首尾多余空格
    return text.strip()

def convert_date_format(text):
    """
    将类似 00.20160727 格式的字符串替换为 2016-07-27 格式
    """
    # 直接使用正则表达式进行替换，不验证日期有效性
    # 匹配模式：(\d{1,2}\.)  - 捕获序号和点号部分
    #          (\d{4})     - 捕获年份部分
    #          (\d{2})     - 捕获月份部分
    #          (\d{2})     - 捕获日期部分
    return re.sub(r"(\d{1,2}\.)(\d{4})(\d{2})(\d{2})", r"【\2-\3-\4】", text)

def ends_sentence(text):
    """
    判断段落是否完整（末尾是否有句号/问号/感叹号等）
    忽略末尾空格、引号和括号等符号
    """
    text = text.strip()
    if not text:
        return True  # 空段落当作结束
    # 去掉末尾的引号、括号、右半标点
    text = re.sub(r"['”』」】〉\)\]]*$", "", text)
    
    # 如果段落末尾不是标点符号，则不认为是完整句子
    if not re.search(fr"[{PUNCTUATION}]$", text):
        return False
    
    # 特殊处理：如果以省略号结尾，但不是以句号、问号或感叹号结尾，则不认为是完整句子
    if re.search(r"[…]{2,}$", text) and not re.search(r"[。！？!?]$", text):
        return False
        
    # 检查是否以句号、问号、感叹号等结尾
    sentence_endings = r"[。！？!?]$"
    return bool(re.search(sentence_endings, text))

def process_html(content):
    """
    合并被错误拆分的段落，并压缩段内空白
    """
    soup = BeautifulSoup(content, "lxml")

    # 删除 <br> 标签
    for br in soup.find_all("br"):
        br.decompose()

    paragraphs = soup.find_all("p")
    merged_paragraphs = []
    buffer_text = ""
    buffer_tag = None

    for p in paragraphs:
        text = p.get_text(separator='', strip=True)
        
        # 如果是空段落，跳过处理
        if not text:
            continue
            
        # 移除全角空格和其他特殊空白字符
        text = re.sub(r'[\u3000\xa0]', ' ', text)

        if buffer_tag is None:
            buffer_tag = p
            buffer_text = text
        else:
            # 改进的判断逻辑：
            # 1. 如果缓冲区文本不以句子结尾符号，则继续合并
            if not ends_sentence(buffer_text):
                # 在段落间添加空格以确保文本正确连接
                buffer_text += " " + text
                # 将当前标签也加入待删除列表，因为它的内容已被合并
                p.decompose()  # 直接从soup中移除该标签
            else:
                merged_paragraphs.append((buffer_tag, buffer_text))
                buffer_tag = p
                buffer_text = text

    if buffer_tag is not None:
        merged_paragraphs.append((buffer_tag, buffer_text))

    # 清空原 <p> 内容并写回合并后的文本
    for tag, text in merged_paragraphs:
        # 先转换日期格式
        text = convert_date_format(text)
        cleaned = tighten_text(text)
        tag.clear()
        tag.append(cleaned)

    return str(soup)

def reformat_epub(input_path, output_path, exclude_items=None):
    if exclude_items is None:
        exclude_items = []
    
    book = epub.read_epub(input_path)

    # 处理目录页(toc)中的日期格式
    if hasattr(book, 'toc'):
        def process_toc_item(item):
            if isinstance(item, list) or isinstance(item, tuple):
                return [process_toc_item(sub) for sub in item]
            elif hasattr(item, 'title'):
                item.title = convert_date_format(item.title)
            return item
        book.toc = process_toc_item(book.toc)

    # 获取所有items以便使用tqdm显示进度
    items = list(book.get_items())
    
    # 使用tqdm显示处理进度，并动态显示当前处理的item名称
    with tqdm(total=len(items), desc="Processing EPUB items", unit="item") as pbar:
        for item in items:
            # 使用set_description动态更新当前处理的item名称
            pbar.set_description(f"Processing: {item.get_name()}")
            
            # 检查是否需要排除当前item
            if item.get_name() in exclude_items:
                pbar.update(1)
                continue
            
            if item.media_type == "application/xhtml+xml":
                html = item.get_content().decode("utf-8")
                # 对整个HTML内容进行日期格式转换
                html = convert_date_format(html)
                processed_html = process_html(html)
                item.set_content(processed_html.encode("utf-8"))
            
            # 更新进度条
            pbar.update(1)

    epub.write_epub(output_path, book)
    print(f"排版完成！生成文件：{output_path}")

def main():
    parser = argparse.ArgumentParser(description="EPUB编辑器：合并段落并转换日期格式")
    parser.add_argument("input", help="输入EPUB文件路径")
    parser.add_argument("output", help="输出EPUB文件路径")
    parser.add_argument("-e", "--exclude", nargs='+', default=[], 
                        help="要排除处理的item名称（多个名称用空格分隔）")
    
    args = parser.parse_args()
    
    reformat_epub(args.input, args.output, args.exclude)

if __name__ == "__main__":
    main()