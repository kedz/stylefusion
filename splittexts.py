from pycorenlp import StanfordCoreNLP
from collections import OrderedDict

Cf = [["although"], ["since"], ["in", "addition", "to"], ["aside", "from"]]
Cs = [
    [",",  "because"],  
    ["because",],  
    ["hence"],  
    [",",  "while"],  
    ["whereas"], 
    [",", "although"],
    ["and", "although"], 
    ["although"],
    ["unless"],
    [",", "now that"], 
    ["now", "that"],
    ["so", "that"], 
    [",", "so", "that"],
    ["meaning"],
    [",", "meaning"],
]

verbs = set(["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"])
rel_pron = ['who', 'which', 'whose', 'whom']

def check_match(s, p, i):
    sub_s = s[i:i+len(p)]
    return sub_s == p

def check_forward_connective(s):
    tokens = [t['word'].lower() for t in s['tokens']]
    n = len(tokens)
    i = 0
    for c in Cf:
        if check_match(tokens, c, i) and "," in tokens[i+len(c):]:
            j = i + len(c) + tokens[i+len(c):].index(",")
            return c, j

def apply_forward_connective(s, fc, comma_idx):
    prefix = clean_span(s, len(fc), comma_idx)
    suffix = clean_span(s, comma_idx+1)
    prefix = fix_terminal_punctuation(prefix)
    prefix = fix_init_capital(prefix)
    suffix = fix_init_capital(suffix)
    return ("forward connective", " ".join(fc)), prefix, suffix

def check_intrasentence_connective(s):
    tokens = [t['word'].lower() for t in s['tokens']]
    n = len(tokens)
    for i in range(n):
        for c in Cs:
            if check_match(tokens, c, i):
                return c, i
     
def apply_intrasentence_connective(s, con, con_idx):
    prefix = clean_span(s, 0, con_idx)
    prefix = fix_terminal_punctuation(prefix)
    prefix = fix_init_capital(prefix)
    suffix = clean_span(s, con_idx + len(con))
    suffix = fix_init_capital(suffix)
    return (("intra-sentence connective", " ".join(con)), prefix, suffix)

def check_cataphora(s):
    pos = (s['tokens'][0]['pos'])

    #for d in s['basicDependencies']:
    #    print(d)

    label = [x['dep'] for x in s['basicDependencies'] if x['dependent'] == 1][0]
    if pos != "VBG" or label != "advcl":
        return
    comma_idx = None
    for i, token in enumerate(s['tokens']):
        if token['originalText'] == ',':
            comma_idx = i
            break
    if comma_idx is None:
        return 
    if s['tokens'][comma_idx + 2]['pos'] in verbs:
        return (comma_idx,)

def apply_cataphora(s, comma_idx):
    subj = s['tokens'][comma_idx + 1]['originalText']

    # TODO handle irregular verbs 
    verb = (s['tokens'][0]['originalText'][:-3] + 'ed').lower()

    cat_phrase = clean_span(s, 1, comma_idx)

    sentA = f'{subj} {verb} {cat_phrase}'
    sentA = fix_terminal_punctuation(sentA)
    sentA = fix_init_capital(sentA)

    sentB = clean_span(s, comma_idx + 1)
    sentB = fix_init_capital(sentB)
    return ('cataphora',), sentA, sentB

def check_conjunction(s):

    deps = sorted(s['basicDependencies'], key=lambda x: x['dependent'])
    assert len(deps) == len(set([x['dependent'] for x in deps]))

    n = len(deps)

    for i in range(n):
        if deps[i]['dep'] != 'cc':
            continue
        conj = None
        for j in range(i+1, min(i+6, n)):
            if deps[j]['dep'] == 'conj':
                conj = j
        if conj == None:
            continue
        for k in range(i+1, j):
            if deps[k]['dep'] in ['nsubj', 'nsubjpass']:
                return s['tokens'][i]['originalText'], i

def apply_conjunction(s, conj, conj_idx):
    sentA = clean_span(s, 0, conj_idx)
    sentA = fix_init_capital(sentA)
    sentA = fix_terminal_punctuation(sentA)
    sentB = clean_span(s, conj_idx + 1)
    sentB = fix_init_capital(sentB)
    return ("conjunction", conj), sentA, sentB

def check_apposition(s):
    deps = sorted(s['basicDependencies'], key=lambda x: x['dependent'])
    n = len(s['tokens'])
    for dep in s['basicDependencies']:
        if dep['dep'] == 'appos':
            k = dep['dependent']
            for i in range(k-1, -1, -1):
                if s['tokens'][i]['originalText'] == ',':
                    for j in range(k+1, n):
                        if s['tokens'][j]['originalText'] == ',':
                            if deps[i+1]['dep'] in ['det', 'poss']:
                                return i,j

def apply_apposition(s, start, stop):
    subj = clean_span(s, 0, start)
    appos = clean_span(s, start + 1, stop)
    predicate = clean_span(s, stop + 1)
    sentA = f'{subj} {predicate}'
    sentB = f'{subj} is {appos}'
    sentB = fix_terminal_punctuation(sentB)
    return ("apposition",), sentA, sentB

def check_relative_clause(s):
    n = len(s['tokens'])
    for k, t in enumerate(s['tokens']):
        if t['originalText'] in rel_pron and k > 0:
            i = k - 1
            if s['tokens'][i]['originalText'] == ',':    
                for j in range(k+1, n):
                    if s['tokens'][j]['originalText'] == ',':
                        return (t['originalText'], i, j)

def apply_relative_clause(s, rp, i, j):
    subj = clean_span(s,0,i)
    rel_clause = clean_span(s, i + 2, j)
    predicate = clean_span(s, j + 1)
    sentA = fix_terminal_punctuation(f'{subj} {rel_clause}')
    sentB = f'{subj} {predicate}'
    return ('relative_clause', rp), sentA, sentB

def check_verb_phrase_coordination(s):
    deps = sorted(s['basicDependencies'], key=lambda x: x['dependent'])
    for i, t in enumerate(s['tokens']):
        if deps[i]['dep'] == 'cc':
            for j in range(i+1, min(i + 6, len(s['tokens']))):
                if deps[j]['dep'] == 'conj' and s['tokens'][j]['pos'] in verbs:
                    if deps[deps[j]['governor']-1]['dep'] == 'ROOT':
                        k = deps[j]['governor']-1
                        return ("verb_phrase_coordination", t['originalText']), i, k

def apply_verb_phrase_coordination(s, cc, i, k):
    A = clean_span(s, 0, i) 
    A = fix_terminal_punctuation(A)
    B = clean_span(s, 0, k) + " " + clean_span(s, i + 1)
    return cc, A, B

def fix_terminal_punctuation(x):
    if x[-1] in ",;":
        return x[:-1] + '.'
    else:
        return x + '.'

def fix_init_capital(x):
    if x[0].isupper():
        return x
    else:
        return x[0].upper() + x[1:]

def clean_span(sent, i, j=None):
    if j is None:
        j = len(sent['tokens'])
    toks = sent['tokens'][i:j]
    strings = [x['before'] + x['originalText'] for x in toks]
    return ''.join(strings).strip()

RULES = (
    ('forward connective', check_forward_connective, apply_forward_connective),
    ('intra-sentence connective', check_intrasentence_connective, apply_intrasentence_connective),
    ('cataphora', check_cataphora, apply_cataphora),
    ('conjunction', check_conjunction, apply_conjunction),
    ('verb phrase coordination', check_verb_phrase_coordination, apply_verb_phrase_coordination),
    ('relative clause', check_relative_clause, apply_relative_clause),
    ('apposition', check_apposition, apply_apposition),

)
ORD_RULES = OrderedDict()
for name, check, application in RULES:
    ORD_RULES[name] = {'check': check, 'apply': application}

class SplitTexts:
    def __init__(self, port):
        self._cnlp = StanfordCoreNLP(f'http://localhost:{port}')
   
    def preprocess(self, text, anaphora=False):
        properties = {
            'annotators': 'parse,lemma' + (',coref' if anaphora else ''), 
            'outputFormat': 'json',
        }
        return self._cnlp.annotate(text, properties=properties)

    def anaphora(self, s1, s2):
        text = "\n".join([s1, s2])
        data = self.preprocess(text, anaphora=True)

        tags = [x['pos'] for x in data['sentences'][1]['tokens']]
        tokens = [x['before'] + x['originalText'] for x in data['sentences'][1]['tokens']]
        for refid in data['corefs'].keys():
            if data['corefs'][refid][0]['sentNum'] != 1:
                continue
            if data['corefs'][refid][0]['type'] == 'PRONOMINAL':
                continue

            for ref in data['corefs'][refid][1:]:
                if ref['sentNum'] != 2:
                    continue
                if ref['type'] != 'PRONOMINAL':
                    continue
                for i in range(ref['startIndex']-1, ref['endIndex']-1):
                    tokens[i] = '@@@@'
                
                idx = ref['startIndex']-1

                tokens[idx] = ' ' + data['corefs'][refid][0]['text']
                if tokens[idx].startswith(' The '):
                    tokens[idx] = ' the ' + tokens[idx][5:]
                if tokens[idx].startswith(' A '):
                    tokens[idx] = ' a ' + tokens[idx][3:]

                if tags[idx] == 'PRP$':
                    
                    if tokens[idx].endswith('s'):
                        tokens[idx] += "'"
                    else:
                        tokens[idx] += "'s"

        tokens = [x for x in tokens if x != '@@@@'] 
        return fix_init_capital(''.join(tokens).strip())
            

    def apply_rules(self, text, data=None):

        if not data:
            data = self.preprocess(text)

        results = []

        for s in data['sentences']:
            rule_matched = False
            for name, rule in ORD_RULES.items():
                check = rule['check'](s)
                if check:
                    result = rule['apply'](s, *check)
                    result = result[:2] + (self.anaphora(*result[1:]),)
                    results.append(result)
                    
                    rule_matched = True
                    break

            if not rule_matched:
                results.append((None, clean_span(s, 0)))
            

        return results

    def recursive_apply(self, text):
       
        data = self.preprocess(text)


        sents = [clean_span(x, 0) for x in data['sentences']]

        from collections import OrderedDict, deque
        results = OrderedDict()


        queue = deque()


        for i, sent in enumerate(sents, 1):
            item = {
                "text": sent,
                "rule": None,
                "splits": None,
            }
            results[i] = item
            queue.append(item)

        while queue:

            item = queue.popleft()
            r = self.apply_rules(item['text'])[0]
            if r[0] is None:
                continue
            next_items = OrderedDict()
            next_items[1] = {
                "text": r[1],
                "rule": None,
                "splits": None,
            }
            next_items[2] = {
                "text": r[2],
                "rule": None,
                "splits": None,
            }
            queue.append(next_items[1])
            queue.append(next_items[2])
            item['splits'] = next_items
            item['rule'] = r[0]


        return results










        
        
#        [
#            "rule": "original",
#            "1": {
#                "text": ".... ",
#                "rule": "conjunction",
#                "splits": {
#                    "1": {
#
#                    },
#                    "2": {
#
#
#                    },
#
#                }
#
#
#
#        original
#         
#        print(text)
#        print() 
#        results = self.apply_rules(text)
#        print("\n".join([str(r[0]) + "  " + x for r in results for x in r[1:]]))
#        next_text = "\n".join([x for r in results for x in r[1:]])
#        while any([x[0] for x in results]):
#            text = next_text
#            results = self.apply_rules(text)
#            print("\n".join([str(r[0]) + "  " +  x for r in results for x in r[1:]]))
#            next_text = "\n".join([x for r in results for x in r[1:]])
#            print()
#
