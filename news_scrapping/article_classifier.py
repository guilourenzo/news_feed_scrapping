class ArticleClassifier:
    def __init__(self):
        self.keywords = {
            'finance': ['economia', 'mercado', 'finanças', 'investimento'],
            'politics': ["lei", "crédito", "proposta", "projeto", "política", "governo", "eleições", "congresso"],
            'sports': ['esporte', 'futebol', 'basquete', 'olimpíadas', "vôlei"],
            'entertainment': ['entretenimento', 'celebridades', 'filmes', 'música'],
            'technology': ['tecnologia', 'inovação', 'startup', 'internet', "apple", "twitter", "google"]
        }

    def classify_article(self, title, description):
        content = title + ' ' + description
        for category, keywords in self.keywords.items():
            if any(keyword in content.lower() for keyword in keywords):
                return category.capitalize()
        return 'Other'
