from neo4jrestclient import client

import application.Library.Constant.GeneralConstant as GeneralConstant

try:
    db = client.GraphDatabase("http://localhost:7474", username="neo4j", password="123456")  # neo4j
except Exception as e:
    print('[General Repository] Failed in loading Neo4j with error: {0}'.format(e.args[0]))
    exit()


def get_date(current_date):
    """
    GET date
    :param current_date:
    :return:
    """
    result = False
    # Store keyword into Neo4j
    try:  # Check if keyword is existed
        query = "MATCH (dat:Date) WHERE dat.date='{0}' " \
                "RETURN dat".format(current_date)
        results = db.query(query, returns=(client.Node, str, client.Node))
        if results.elements:
            result = results.elements[0][0]
    except Exception as e:
        print('[Generate Date] Failed in storing date into Neo4j with error: {0}'.format(e.args[0]))
    return result


# Get category in neo4j
def get_category():
    """
    GET category from neo4j
    :return:
    """
    print("Getting categories in Neo4j")
    result = {}
    try:
        query = "MATCH (cat: Category) RETURN cat"
        data = db.query(query, returns=(client.Node, str, client.Node))
        if not data.elements:
            try:
                # Create category nodes
                category = db.labels.create("Category")

                cat = [db.nodes.create(name="CongNghe", sign="CN"), db.nodes.create(name="GiaoDuc", sign="GD"),
                       db.nodes.create(name="KhoaHoc", sign="KH"), db.nodes.create(name="PhapLuat", sign="PL"),
                       db.nodes.create(name="TheGioi", sign="TG"), db.nodes.create(name="ThoiSu", sign="TS")]
                for element in cat:
                    category.add(element)
                print('[Migrating Categories] Storing categories into Neo4j successfully')
                data = db.query(query, returns=(client.Node, str, client.Node))
            except Exception as e:
                print(
                    '[Migrating Categories] Failed in storing categories into Neo4j with error: {0}'.format(e.args[0]))
                return False
        print("Getting categories from Neo4j successfully")
        for element in data:
            result[element[0]['name']] = element[0]  # add to category node array
        return result
    except Exception as e:
        print('[Get Categories] Failed in getting categories from Neo4j with error: {0}'.format(e.args[0]))
        return False


# Get keywords by category and date
def get_papers_by_category_and_date(category, from_date='0', to_date='0'):
    """
    GET paper by category and date
    :param category:
    :param from_date: > date
    :param to_date: = date
    :return:
    """
    # Query data from Neo4j
    if to_date != '0':
        query = "MATCH (cat:Category)-[]->(pap:Paper) WHERE cat.name='{0}' " \
                "WITH collect(pap) as paper MATCH (dat:Date)-[]->(pap:Paper) " \
                "WHERE dat.date>'{1}' AND dat.date<='{2}' AND pap in paper " \
                "RETURN pap".format(category, from_date, to_date)
    else:
        query = "MATCH (cat:Category)-[]->(pap:Paper) WHERE cat.name='{0}' " \
                "WITH collect(pap) as paper MATCH (dat:Date)-[]->(pap:Paper) " \
                "WHERE dat.date='{1}' AND pap in paper " \
                "RETURN pap".format(category, from_date)

    try:
        return db.query(query, returns=(client.Node, str, client.Node))
    except Exception as e:
        print('[get_papers_by_category_and_date] Failed in retrieving papers from neo4j: {0}'.format(e.args[0]))
        return False


# Get paper by path id
def get_paper_by_path_id(path_id):
    """
    get_paper_by_path_id
    :param path_id:
    :return:
    """
    result = {'code': GeneralConstant.RESULT_FALSE(), 'data': None}
    try:
        query = " MATCH (pap: Paper) WHERE pap.path CONTAINS '{0}' RETURN pap".format(path_id)
        paper_node = db.query(query, returns=(client.Node, str, client.Node))

        result['code'] = GeneralConstant.RESULT_TRUE()
        result['data'] = paper_node.elements[0][0]
    except Exception as e:
        print('[get_paper_by_path_id] Failed in retrieving paper from neo4j: {0}'.format(e.args[0]))
    return result


# Get keywords of a paper
def get_keyword_by_paper_id(paper_id):
    """
    get_keyword_by_paper_id
    :param paper_id:
    :return:
    """
    result = {'code': GeneralConstant.RESULT_FALSE(), 'data': None}
    try:
        query = "MATCH (key:Keyword)<-[ptk:PaperToKeyword]-(pap:Paper) WHERE id(pap)={0} RETURN key.name as name, " \
                "ptk.weight as weight".format(int(paper_id))
        keyword_node = db.query(query)

        result['code'] = GeneralConstant.RESULT_TRUE()
        columns = keyword_node.get_response()['columns']
        data = keyword_node.get_response()['data']
        keywords = []
        for item in data:
            row = {columns[0]: item[0], columns[1]: item[1]}
            keywords.append(row)
        result['data'] = keywords
    except Exception as e:
        print('[get_keyword_by_paper_id] Failed in retrieving paper from neo4j: {0}'.format(e.args[0]))
    return result


# Create paper node
def create_paper_node(paper_name, original_paper_path, processed_paper_path, paper_sentences, category_nodes,
                      current_category, current_date_node):
    """
    CREATE paper in Neo4j
    :param paper_name:
    :param original_paper_path:
    :param processed_paper_path:
    :param paper_sentences:
    :param category_nodes:
    :param current_category:
    :param current_date_node:
    :return:
    """
    result = {}
    result['code'] = GeneralConstant.RESULT_FALSE()
    paper_nodes = db.labels.create("Paper")  # paper nodes
    try:
        # Check if paper is existed
        query = "MATCH (pap:Paper) WHERE pap.name='{0}' " \
                "RETURN pap".format(paper_name)
        current_paper_node = db.query(query, returns=(client.Node, str, client.Node))
        if not current_paper_node.elements:
            # Save each paper to database
            current_paper_node = db.node.create(name=paper_name, path=original_paper_path,
                                                sentence=paper_sentences, processed_paper_path=processed_paper_path)
            paper_nodes.add(current_paper_node)  # update label for paper
            # create relationship from category to paper
            category_nodes[current_category].relationships.create("CategoryToPaper", current_paper_node)
            # create relationship from date to paper
            current_date_node.relationships.create("DateToPaper", current_paper_node)
            result['data'] = current_paper_node
            result['code'] = GeneralConstant.RESULT_TRUE()
        else:
            result['code'] = GeneralConstant.DELETE_PAPER()

        # # Save each paper to database
        # current_paper_node = db.node.create(title=paper_title, path=original_paper_path,
        #                                     sentence=paper_sentences, processed_paper_path=processed_paper_path)
        # paper_nodes.add(current_paper_node)  # update label for paper
        #
        # # create relationship from category to paper
        # category_nodes[current_category].relationships.create("CategoryToPaper", current_paper_node)
        # # create relationship from date to paper
        # current_date_node.relationships.create("DateToPaper", current_paper_node)
        # result['data'] = current_paper_node
        # result['code'] = True
    except Exception as e:
        import os
        print('[create_paper_node] Failed storing at paper: {0} with errors: {1}'.format(
            os.path.basename(original_paper_path).replace('.txt', ''), e.args[0]))
    return result


# Create date node
def create_date_node(current_date, processed_date_path):
    """
    CREATE date in Neo4j
    :param processed_date_path:
    :param current_date:
    """
    result = {}
    result['code'] = GeneralConstant.RESULT_FALSE()
    date_nodes = db.labels.create("Date")  # date nodes
    try:
        # Check if date is existed
        query = "MATCH (date:Date) WHERE date.date='{0}' " \
                "RETURN date".format(current_date)
        current_date_node = db.query(query, returns=(client.Node, str, client.Node))
        if not current_date_node.elements:
            current_date_node = db.node.create(date=current_date, processed_date_path=processed_date_path)
            date_nodes.add(current_date_node)
        else:
            current_date_node = current_date_node.elements[0][0]
        result['code'] = GeneralConstant.RESULT_TRUE()
        result['data'] = current_date_node
    except Exception as e:
        print('[create_date] Failed with error: {0}'.format(e.args[0]))
    return result


# Create keyword node
# def create_keyword_node(keyword_name, current_category_node, current_date):
#     """
#     GET keyword by name
#     :param keyword_name:
#     :return:
#     """
#     keyword_node = db.labels.create("Keyword")  # date nodes
#     result = False
#     # Store keyword into Neo4j
#     try:
#         # Check if keyword is existed
#         query = "MATCH (key:Keyword) WHERE key.name='{0}' " \
#                 "RETURN key".format(keyword_name)
#         current_keyword_node = db.query(query, returns=(client.Node, str, client.Node))
#         if current_category_node is not None and current_date is not None:
#             # Create new keywords
#             if not current_keyword_node.elements:
#                 current_keyword_node = db.node.create(name=keyword_name)  # create keyword node
#                 keyword_node.add(current_keyword_node)
#             # Create relationship
#             current_category_node.relationships.create('CategoryToKeyword', current_keyword_node, date=current_date)
#             result = current_keyword_node
#     except Exception as e:
#         print('[Generate Keyword] Failed in storing keywords into Neo4j with error: {0}'.format(e.args[0]))
#     return result
def create_keyword_node(keyword, current_paper_path_id, category_nodes, current_category, current_date):
    """
    GET keyword by name
    :param category_nodes:
    :param current_category:
    :param keyword:
    :param current_paper_path_id:
    :param current_date:
    :return:
    """
    keyword_node = db.labels.create("Keyword")  # date nodes
    result = {'code': GeneralConstant.RESULT_FALSE(), 'data': None}
    keyword_name, keyword_weight = keyword
    # Store keyword into Neo4j
    try:
        if current_category is not None and current_date is not None:
            # Check if keyword is existed
            query = "MATCH (key:Keyword) WHERE key.name='{0}' " \
                    "RETURN key".format(keyword_name)
            current_keyword_node = db.query(query, returns=(client.Node, str, client.Node))
            # Create new keywords
            if not current_keyword_node.elements:
                current_keyword_node = db.node.create(name=keyword_name)  # create keyword node
                keyword_node.add(current_keyword_node)
            else:
                current_keyword_node = current_keyword_node.elements[0][0]
            # Create relationship
            category_nodes[current_category].relationships.create('CategoryToKeyword', current_keyword_node,
                                                                  date=current_date)
            current_paper_node = get_paper_by_path_id(current_paper_path_id)['data']  # get current_paper_node
            current_paper_node.relationships.create('PaperToKeyword', current_keyword_node, weight=keyword_weight)

            result = {'code': GeneralConstant.RESULT_TRUE(), 'data': current_keyword_node}
    except Exception as e:
        print('[create_keyword_node] Failed in generate keywords into Neo4j with error: {0}'.format(e.args[0]))
    return result


# load category
category_nodes = get_category()
