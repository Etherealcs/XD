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

    def predict(self, prompt: str) -> str:
        #llm = ChatOpenAI(api_key="sk-proj-8WDPTIBAZyUIpTcc7XDXT3BlbkFJk49DFk0x8C4oZVDkYwgv", model="gpt-3.5-turbo", temperature=0.5, streaming=True)
        llm = Ollama(model="glm4:9b", temperature=0.5, num_ctx=50000)
        response = llm.invoke(prompt)
        message_content = response
        """response = openai_client.chat.completions.create(
            model='gpt-3.5-turbo',  # Use the appropriate model name, e.g., 'gpt-4'
            messages=[{"role": "user", "content": prompt}],
            temperature=0.95,
            max_tokens=4096,
        )"""
        #message_content = response.choices[0].message.content
        """response = zhipu_client.chat.completions.create(
            model='glm-4-9b',
            messages=[{"role": "user", "content": prompt}],
            temperature=0.95,
            max_tokens=8192,
        ).choices[0].message.content"""
        return message_content

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
                print("JSON decode error")
                return []
        else:
            print("No JSON content found")
            print("应用尚处于测试阶段，模型可能没有正确解读论文，请再次尝试，以获得正确结果！")
            return []

    def get_arxiv_pdf(self, pdf_link: str) -> str:
        result = subprocess.run(['curl', f'https://r.jina.ai/{pdf_link}'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error: {result.stderr}")
            return None

    def run(self) -> list:
        result = []
        for website in self.websites:
            web_content = self.fetch_papers(website)
            if web_content:
                web_summary = self.predict(self.GET_ARXIV_PAPER.format(web_content=web_content))
                print("web_summary",web_summary)
                json_data = self.parse_json(web_summary)
                print("json_data",json_data)
                for paper in json_data:
                    pdf_content = self.get_arxiv_pdf(paper['link'])
                    if pdf_content:
                        pdf_summary = self.predict(self.GET_ARXIV_PDF.format(content=pdf_content))
                        paper['summary'] = pdf_summary
                result.append(json_data)
        print("task done!")
        return result


trigger = Trigger(websites=['https://export.arxiv.org/api/query?search_query=llm&sortBy=submittedDate&sortOrder=descending&max_results=2'])
papers_summary = trigger.run()
print("summary:",papers_summary)
"""with open('output.jsonl', 'w', encoding='utf-8') as file:
    for i in papers_summary:
        for item in i:
            json_str = json.dumps(item, ensure_ascii=False)
            file.write(json_str + '\n')"""