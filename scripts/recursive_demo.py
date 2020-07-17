import shutil
import textwrap

from splittexts import SplitTexts


def pretty_print(results, indent=''):
    cols, _ = shutil.get_terminal_size((80, 20))

    for key, result in results.items():
        
        print(
            textwrap.fill(
                f"({key})  {result['text']}",
                width=cols,
                initial_indent=indent,
                subsequent_indent=indent + "        "))

        if result['rule']:
            print(indent + "  |   ")
            print(indent + "  +-> " + str(result['rule']))
            pretty_print(result['splits'], indent + "    ")

def print_original(results):
    cols, _ = shutil.get_terminal_size((80, 20))
    for i, result in enumerate(results.values(), 1):
         print(
            textwrap.fill(
                f"({i})  {result['text']}",
                width=cols,
                initial_indent="    ",
                subsequent_indent="        "))

def print_final_splits(results):
    
    def collect_sentences(item):
        if item['rule']:
            r = []
            r.extend(collect_sentences(item['splits'][1]))
            r.extend(collect_sentences(item['splits'][2]))
            return r

        else:
            return [item['text']]

    r = []
    for item in results.values():
        r.extend(collect_sentences(item))

    cols, _ = shutil.get_terminal_size((80, 20))
    for i, sent in enumerate(r, 1):
         print(
            textwrap.fill(
                f"({i})  {sent}",
                width=cols,
                initial_indent="    ",
                subsequent_indent="        "))

def main():
    port = 9000
    splitter = SplitTexts(port)

    example = """
Although Toad was thought to be a minor character and not considered key to the story,
he intended to help defeat Bowser, and the Mushroom Kingdom would save the Super Mario
Brothers. He wanted to be brave so that John Darnielle, who had written
a song about him, would not be disappointed.
    """.replace('\n', ' ').strip()

    cols, _ = shutil.get_terminal_size((80, 20))

    print()
    print("The Original String")
    print("===================")
    print()
    print(textwrap.fill(example, width=cols - 4, initial_indent="    ", subsequent_indent="    "))
    print()

    results = splitter.recursive_apply(example)

    print("Pretty print recursive splitting")
    print("================================")
    print()
    pretty_print(results, "    ")
    print()

    print("Original sentences from recursive split results")
    print("===============================================")
    print()
    print_original(results)
    print()

    print("Fully decomposed sentences from recursive split results")
    print("=======================================================")
    print()
    print_final_splits(results)
    print()

if __name__ == "__main__":
    main()
