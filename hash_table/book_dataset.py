import re
import urllib.request


class BookDataset:
    
    def __init__(self, url="https://www.gutenberg.org/files/98/98-0.txt", output_file="98-0.txt"):
        self.url = url
        self.output_file = output_file
        self.word_freq = {}
    
    def create(self):
        """Download book and create word frequency map."""
        content = self._download_book()
        words = self._extract_words(content)
        self.word_freq = self._create_frequency_map(words)
        
        print(f"Total words: {len(words)}")
        print(f"Unique words: {len(self.word_freq)}")
        
        return self.word_freq
    
    # === Helper Methods ============================================================

    def _download_book(self):
        """Download the book from Project Gutenberg."""
        print(f"Downloading book from {self.url}...")
        try:
            with urllib.request.urlopen(self.url) as response:
                content = response.read().decode('utf-8')
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Book saved to {self.output_file}")
        except Exception as e:
            print(f"Error: {e}. Reading from local file...")
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
        return content
    
    def _extract_words(self, text):
        """Extract words from text."""
        lines = text.split('\n')
        start_idx = 0
        end_idx = len(lines)
        
        for i, line in enumerate(lines):
            if 'START OF THE PROJECT GUTENBERG EBOOK' in line:
                start_idx = i + 1
                break
        
        for i in range(len(lines) - 1, -1, -1):
            if 'END OF THE PROJECT GUTENBERG EBOOK' in lines[i]:
                end_idx = i
                break
        
        text = '\n'.join(lines[start_idx:end_idx])
        return re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    def _create_frequency_map(self, words):
        """Create word frequency map."""
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        return word_freq