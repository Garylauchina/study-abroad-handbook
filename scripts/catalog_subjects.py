"""Editorial browsing tags; these do not claim an official subject classification."""
import re

RULES = [
    ('计算机', r'computer|computing|informatics|informatik|informatique|software|cyber|artificial intelligence|data science|人工智能|计算机|電腦|计算|資訊|情報|软件|情報|データ'),
    ('医学与健康', r'medicine|medical|medicin|médec|medizi|nurs|denti|dentist|dental|odont|pharma|physiotherap|occupational therap|midwif|health|veterin|kinesiolog|optometr|nutrition|rehabilit|醫|医学|护理|健康|薬|薬学|看護'),
    ('法律', r'\blaw\b|laws|legal|juris|recht|droit|abogac|derecho|法律|法学|法學'),
    ('艺术与设计', r'fine arts|visual arts|perform|music|musical|theat|theater|cinema|film|dance|design|fashion|studio art|animation|dram|photograph|sculpt|piano|violin|jazz|composition|vocal|diseño|艺术|藝術|设计|設計|音楽|音樂|미술|음악'),
    ('教育', r'education|teaching|pedagog|pédagog|profesor|erziehung|lehramt|教育'),
    ('工程', r'engineer|ingénieur|ingenier|ingenieur|ingegner|architecture|architektur|architectural|robotic|aeronaut|aviation|aerospace|construction|工程|工学|工學|建築|建筑'),
    ('经济', r'economic|économie|economía|ökonom|volkswirtschaft|経済|경제|经济|經濟'),
    ('商科', r'business|commerce|commerc|management|accounting|finance|financial|marketing|entrepreneur|actuar|wirtschaft|comptab|administración|administration|商学|商學|会计|會計|金融|经营|経営|경영'),
    ('环境与农业', r'environ|sustainab|agricultur|agronom|forestr|food science|earth|geolog|geophys|ecolog|climate|marine|ocean|ressourc|environment|ambient|農|农业|環境|环境|地球'),
    ('数学与统计', r'math|statistic|statistics|mathemati|matemática|数学|數學|统计|統計|수학'),
    ('自然科学', r'biolog|biochem|biophys|biomolec|chemistr|chemie|chimie|physic|physik|physique|astronom|astrophys|botan|zoolog|genetic|neuroscien|microbio|physiolog|bioinformat|geoscien|molecular|biotechnolog|生物|化学|化學|物理|天文'),
    ('社会科学', r'psycholog|sociolog|anthropolog|politic|social|communication|journalis|criminolog|international relations|public policy|geograph|global studies|gender|gender|social work|社会|社會|心理|政治|传播|傳播'),
    ('人文', r'histor|philosoph|literatur|linguistic|language|english|french|german|spanish|italian|portuguese|chinese|japanese|korean|arabic|hebrew|latin|greek|classics|classical|religio|theolog|archaeolog|archäolog|archéolog|cultural|humanities|medieval|african|asian|americ|european|russian|slavic|sanskrit|traduct|翻译|翻譯|语言|語言|語学|文学|文學|哲学|哲學|历史|歷史'),
]


def classify(name):
    tags = [label for label, pattern in RULES if re.search(pattern, name, re.I)]
    return tags or ['待分类']
