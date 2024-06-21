# config.py
newspaper_configs = {
    'HK': {
        'title_tag': 'h1',
        'title_class': 'headline',
        'main_section_tag': 'div',
        'main_section_class': 'article-body',
        'paragraph_tag': ['p', 'br'],
    },
    'MK': {
        'title_tag': 'h2',
        'title_class': 'news_ttl',
        'main_section_tag': 'div',
        'main_section_class': 'news_cnt_detail_wrap',
        'paragraph_tag': 'p',
        'paragraph_attr': {'refid': True},
    }
}
