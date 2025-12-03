
## How It Works 🔧

1. **Paragraph Merging Algorithm**:
   - Detects incomplete sentences by analyzing ending punctuation
   - Handles special cases like ellipsis (...) that may indicate continuation
   - Preserves proper paragraph breaks while merging fragmented content

2. **Date Conversion**:
   - Finds patterns matching `XX.YYYYYYYY` format
   - Extracts YYYY MM DD components
   - Reformats to ISO standard `YYYY-MM-DD` with surrounding brackets 【】
   - Applies conversion to both content and table of contents

3. **Processing Pipeline**:
   - Reads EPUB file structure
   - Processes each XHTML item with progress tracking
   - Applies transformations while preserving document integrity
   - Writes cleaned content to new EPUB file

## Example Transformations ✨

### Before:
```html
<p>Why do many plans ultimately fail to materialize and fade away? The deepest reason may be that your life cycle at the time...</p>
<p>的种种周期（比如经济周期）都各不相同，于是，没有人能帮你具体地定制完全适合你的计划…… 所以，最终，人生规</p>
<p>划这种东西，听不得别人的，必须自己来，否则也没办法后果自负。</p>
```

### After:
```html
<p>Why do many plans ultimately fail to materialize and fade away? The deepest reason may be that your life cycle at the time... 的种种周期（比如经济周期）都各不相同，于是，没有人能帮你具体地定制完全适合你的计划…… 所以，最终，人生规划这种东西，听不得别人的，必须自己来，否则也没办法后果自负。</p>
```

### Date Format Conversion:
- `00.20160727` → `【2016-07-27】`

## Contributing 🤝

Contributions are welcome! Feel free to submit issues and pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- Built with [ebooklib](https://github.com/aerkalov/ebooklib)
- HTML parsing powered by [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- Progress tracking by [tqdm](https://github.com/tqdm/tqdm)

---

<p align="center">
  Made with ❤️ for better e-reading experiences
</p>
