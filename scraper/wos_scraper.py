import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def jsonfetch(url):
    req = requests.get(url)
    return req


def soup_extractor(url):
    req = jsonfetch(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup


def data_extractor(columns, tr_rows):
    if tr_rows:
        # Defining different Details URL structure
        detail_types = {
            8: ['Journal Title', 'P-ISSN', 'E-ISSN', 'Publisher', 'Country of Publisher', 'Scope', 'Language',
                'Category'],
            9: ['Journal Title', 'ISSN', 'SJR', 'Journal Quartile', 'H-index', 'Impact Score', 'Publisher',
                'Country', 'Area of Publication'],
            11: ['Journal Title', 'P-ISSN', 'E-ISSN', 'Language', 'Publisher', 'Review Process',
                 'Publication Time (weeks)', 'APC', 'Waiver Policy', 'Area of Publication',
                 'Journal official Website'],
            12: ['Journal Title', 'P-ISSN', 'E-ISSN', 'Language', 'Publisher', 'Review Process',
                 'Publication Time (weeks)', 'APC', 'APC Amount', 'Waiver Policy', 'Area of Publication',
                 'Journal official Website']}
        length = len(columns)
        if (columns.tolist() == detail_types[length]) and length == 8:
            return ['',
                    tr_rows[1].text.strip("\n"),
                    tr_rows[2].text.strip("\n"),
                    tr_rows[6].text.strip("\n"),
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    tr_rows[3].text.strip("\n"),
                    tr_rows[4].text.strip("\n"),
                    tr_rows[5].text.strip("\n"),
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    pd.NA]
        elif (columns.tolist() == detail_types[length]) and length == 9:
            return [tr_rows[1].text.strip("\n"),
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    tr_rows[2].text.strip("\n"),
                    tr_rows[3].text.strip("\n"),
                    tr_rows[4].text.strip("\n"),
                    tr_rows[5].text.strip("\n"),
                    tr_rows[6].text.strip("\n"),
                    tr_rows[7].text.strip("\n"),
                    tr_rows[8].text.strip("\n"),
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    pd.NA]
        elif (columns.tolist() == detail_types[length]) and length == 11:
            return ['',
                    tr_rows[1].text.strip("\n"),
                    tr_rows[2].text.strip("\n"),
                    tr_rows[3].text.strip("\n"),
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    tr_rows[4].text.strip("\n"),
                    pd.NA,
                    tr_rows[9].text.strip("\n"),
                    tr_rows[5].text.strip("\n"),
                    tr_rows[6].text.strip("\n"),
                    tr_rows[7].text.strip("\n"),
                    pd.NA,
                    tr_rows[8].text.strip("\n"),
                    tr_rows[10].text.strip("\n")]
        elif (columns.tolist() == detail_types[length]) and length == 12:
            return ['',
                    tr_rows[1].text.strip("\n"),
                    tr_rows[2].text.strip("\n"),
                    tr_rows[3].text.strip("\n"),
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    pd.NA,
                    tr_rows[4].text.strip("\n"),
                    pd.NA,
                    tr_rows[10].text.strip("\n"),
                    tr_rows[5].text.strip("\n"),
                    tr_rows[6].text.strip("\n"),
                    tr_rows[7].text.strip("\n"),
                    tr_rows[8].text.strip("\n"),
                    tr_rows[9].text.strip("\n"),
                    tr_rows[11].text.strip("\n")]
        else:
            return ['error_not_hit_critera' for i in range(17)]
    else:
        return ['error_False' for i in range(17)]


def page_counter(soup):
    pages = soup.find_all(class_='pagination')[0]
    page_numbers = pages.find_all('a')
    last_number = int(page_numbers[-1].text)

    return last_number


def extract_title(value):
    if pd.isnull(value) or not isinstance(value, str):
        return value
    if ':' in value:
        return value.split(':', 1)[1].strip()  # Split only on the first colon
    return value


def cleaner(df):
    columns_with_semicolon = df.apply(lambda col: col.astype(str).str.contains(':').any())

    other_columns = columns_with_semicolon[~columns_with_semicolon].index.tolist()
    remained_df = df[other_columns]
    cols = columns_with_semicolon[columns_with_semicolon].index.tolist()

    cols.pop(cols.index('best_ranking'))
    selected_cols = df[cols].copy()

    for column in cols:
        selected_cols[column] = selected_cols[column].apply(extract_title)

    cleaned_df = pd.concat([remained_df, selected_cols], axis=1)

    return cleaned_df


class Scraper():
    def __init__(self, directory, country):
        self.directory = directory
        self.country = country

        self.url = "https://wos-journal.info/country?country={}&page={}"
        self.url_details = "https://wos-journal.info/journalid/{}"
        self.url_meta = "https://wosjournal.com/details.php?id={}"

        self.initiate()

    def total_page_numbers(self, url):
        soup = soup_extractor(url.format(self.country, 0))
        last_number = page_counter(soup)
        page_count = 0

        while page_count <= last_number + 1:
            soup = soup_extractor(url.format(self.country, page_count))
            last_number = page_counter(soup)

            page_count += 1

        return page_count

    def information_collector(self, data_dict):
        result_df = pd.DataFrame(columns=['rows', "title", 'category', 'core_citation_index', 'impact_factor_jif',
                                          'impact_factor_5y', 'best_ranking', 'open_access', 'publisher_journalid',
                                          'status', 'issn_jid', 'eissn_jid', 'issn', 'p_issn', 'e_issn', 'language',
                                          'sjr', 'journal_quartile', 'h_index', 'impact_score', 'publisher', 'country',
                                          'publication_area', 'review_process', 'publication_time', 'apc', 'apc_amount',
                                          'waiver_policy', 'website'])

        error_df = pd.DataFrame(columns=['index', 'Error', 'journal_title', 'URL'])

        for key in list(data_dict.keys()):
            # Finding Rows of data in URL
            rows = data_dict[key].find_all(class_="row px-5 py-5")

            for i in range(1,len(rows)):
                card = rows[i]
                journal_id = card.find(class_="content col-8 col-md-9").text.replace("\n", "")[1:]
                journal_title = card.find(class_="content col-8 col-md-9 text-primary").text.replace("\n", "")
                journal_title = journal_title.replace("&", 'and')

                details_soup = soup_extractor(self.url_details.format(journal_id))
                container = details_soup.find_all("div", class_="row px-5 py-5")[0]
                container_divs = container.find_all('div')

                issn_jid = container_divs[4].text.strip("\n")
                eissn_jid = container_divs[6].text.strip("\n")

                category = container_divs[8].text
                dash_loc = category.find('-')
                category = category[:dash_loc - 1].strip("\n")

                core_citation_index = container_divs[10].text.strip("\n")
                impact_factor_jif = container_divs[12].text.strip("\n")
                impact_factor_5y = container_divs[14].text.strip("\n")
                best_ranking = container_divs[16].text.strip("\n")
                open_access = container_divs[18].text.strip("\n")
                status = container_divs[22].text.strip("\n")
                publisher_jid = container_divs[24].text.strip("\n")

                meta_soup = soup_extractor(self.url_meta.format(journal_title))
                table = meta_soup.find(class_="table")

                try:
                    tr_rows = table.find_all("tr")
                    columns = pd.Series([item.text.split(':')[0] for item in table.find_all('b')], name='columns')
                    rows_lengths = len(tr_rows)
                except AttributeError as e:
                    error_df.loc[len(error_df)] = [i, "details URL doesn't exist", journal_title, self.url_meta.format(journal_title)]
                    tr_rows = False
                    columns = False
                    rows_lengths = 'error_tr_rows'

                details_row = data_extractor(columns, tr_rows)

                result_df.loc[len(result_df)] = [rows_lengths,
                                                 journal_title,
                                                 category, core_citation_index, impact_factor_jif, impact_factor_5y, best_ranking, open_access, publisher_jid, status, issn_jid, eissn_jid] + details_row

        return result_df, error_df

    def local_dict_extractor(self, max_num):
        found_dict = {}
        nums_list = range(0, max_num)

        urls = [self.url.format(self.country, num) for num in nums_list]

        n = len(nums_list)

        if n == 0:
            n = 1

        with ThreadPoolExecutor(max_workers=n) as pool:
            responses = list(pool.map(soup_extractor, urls))
            for x, response in zip(nums_list, responses):
                found_dict[x] = response
        return found_dict

    def initiate(self):
        try:
            total_pages = self.total_page_numbers(self.url)
        except IndexError:
            total_pages = 0

        dict_total = self.local_dict_extractor(total_pages)

        results, errors = self.information_collector(dict_total)

        # Save dataframes to CSV files
        results_file = 'results.csv'
        errors_file = 'errors.csv'

        results.to_csv(results_file, index=False)
        errors.to_csv(errors_file, index=False)
