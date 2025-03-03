import subprocess
from langchain_community.llms.ollama import Ollama
import re
import json

class Trigger:
    GET_ARXIV_PAPER = """
    ## Task
    如下是从Arxiv中获取到的文章，请你按照如下json格式总结所有文章的信息并依次返回，不要输出任何其他内容，确保你的输出能够被json.load()方法解析!
    {{
        id: "序号，从1开始",
        title: "论文标题",
        introduction: "论文摘要的中文翻译",
        recommend_reason: "为什么推荐这篇论文的理由",
        link: "论文的pdf文件链接"
    }}
    ## Papers
    {web_content}
    """
    # GPT阅读总结论文内容prompt
    GET_ARXIV_PDF = """
    ## Task
    阅读下面的论文，为用户介绍它们，回答必须使用中文，且包括以下关键信息：
    1. 基本信息：
    - 论文标题、作者、发表日期、发表期刊、关键词
    2. 摘要：
    - 摘要内容：概括论文的整体内容。
    3. 研究背景：
    - 研究的背景和动机：为什么进行这项研究。
    - 研究的主要问题或挑战：研究要解决的问题。
    4. 研究目的：
    - 研究目标：研究的主要目标。
    5. 文献综述：
    - 相关领域已有的研究：总结相关领域已有研究。
    - 本研究的理论基础：本研究是如何建立在之前研究基础上的。
    6. 研究方法：
    - 研究方法和技术：研究中使用的方法和技术。
    - 数据收集和分析：数据是如何收集和分析的。
    7. 研究结果：
    - 主要研究结果：研究发现。
    - 结果与研究目标的关系：结果如何支持研究目标。
    8. 讨论：
    - 研究结果的意义：研究结果的意义和影响。
    - 结果如何解释和支持研究假设：解释研究结果是否支持假设，提供合理的解释。
    - 有哪些意外发现或有趣的结果。
    9. 结论：
    - 研究的主要结论：研究的结论。
    - 研究的局限性：研究的局限。
    - 对未来研究的建议：未来研究的建议和方向。
    10. 参考文献：
    - 关键参考文献：几篇重要的参考文献,不超过5篇。
    11. 研究贡献：
    - 研究对该领域的主要贡献：研究的创新点和贡献。
    12. 实际应用：
    - 研究结果的实际应用：研究结果的实际应用及其对行业或社会的影响。

    ## Content
    {content}
    """
    def __init__(self, websites: list = []) -> None:
        self.websites = websites
        self.llm = Ollama(model="glm4", temperature=0.5, num_ctx=50000)
    def predict(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)
        message_content = response
        return message_content
    def stream_predict(self, prompt: str) -> str:
        res = self.llm.stream(prompt)
        for chunk in res:
            if chunk:
                yield chunk

    def fetch_papers(self, website: str) -> str:
        result = subprocess.run(['curl', website], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error: {result.stderr}")
            return None

    def parse_json(self, text: str) -> list:
        pattern = r'```json(.*)```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            json_text =match.group(1)
            json_text = json_text.strip()
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                #print("JSON decode error")
                raise Exception("应用尚处于测试阶段，模型可能没有正确解读论文，请再次尝试，使用英文直接输入希望阅读的文献类别标签，以获得正确结果！")
                return []
        else:
            #print("No JSON content found")
            raise Exception("应用尚处于测试阶段，模型可能没有正确解读论文，请再次尝试，使用英文直接输入希望阅读的文献类别标签，以获得正确结果！")
            return []

    def get_arxiv_pdf(self, pdf_link: str) -> str:
        result = subprocess.run(['curl',f'https://r.jina.ai/{pdf_link}'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            #print(f"Error: {result.stderr}")
            return None

    def get_summary(self) -> list:
        result = []
        web_content = self.fetch_papers(self.websites)
        if web_content:
            web_summary = self.predict(self.GET_ARXIV_PAPER.format(web_content=web_content))
            #print("web_summary",web_summary)
            json_data = self.parse_json(web_summary)
            #print("json_data", json_data)
            result.append(json_data)
        else:
            raise Exception("该类文献搜索失败，请尝试更换文献标签！")
        return result[0]
    def get_paperdata(self,summary:list)->list:
        result = []
        i=0
        for paper in summary:
            i+=1
            yield f"\n\n\n\n 第{i}篇文献详细信息如下：\n\n\n\n"
            pdf_content = self.get_arxiv_pdf(paper['link'])
            if pdf_content:
                res = self.llm.stream(self.GET_ARXIV_PDF.format(content=pdf_content))
                for chunk in res:
                    if chunk:
                        yield chunk

