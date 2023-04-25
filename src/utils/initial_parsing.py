import sys
from datetime import datetime

sys.path.append('../src')
import utils.parsing as pars

# there could be any other VK group and other amount of posts
number_of_posts_dict = {
    'looksource': 13000,
    'lookcounstructor': 13000,
    'look_sales': 3500
}

for group_name, number_of_posts in number_of_posts_dict.items():
    posts_data = pars.get_group_info(group_name, number_of_posts)
    dateTimeObj = datetime.now()
    filename = f'raw/{group_name}-posts-{number_of_posts}-{dateTimeObj.strftime("%d-%b-%Y")}.json'
    pars.write_json(posts_data, filename, mode='w')