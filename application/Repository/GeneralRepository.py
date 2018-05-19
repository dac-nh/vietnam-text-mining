from neo4jrestclient import client

try:
    db = client.GraphDatabase("http://localhost:7474", username="neo4j", password="123456")  # neo4j
except Exception as e:
    print('[General Repository] Failed in loading Neo4j with error: {0}'.format(e.args[0]))
    exit()


def get_keyword_by_name(keyword_name, current_category_node=None, current_date=None):
    """
    GET keyword by name
    :param keyword_name:
    :return:
    """
    keyword_node = db.labels.create("Keyword")  # date nodes
    result = False
    # Store keyword into Neo4j
    try:  # Check if keyword is existed
        query = "MATCH (key:Keyword) WHERE key.name='{0}' " \
                "RETURN key".format(keyword_name)
        results = db.query(query, returns=(client.Node, str, client.Node))

        # Create new keywords
        if not results.elements and (current_category_node is not None and current_date is not None):
            current_keyword_node = db.node.create(name=keyword_name)  # create keyword node
            keyword_node.add(current_keyword_node)

            # Create relationship
            current_category_node.relationships.create('CategoryToKeyword', current_keyword_node, date=current_date)

            query = "MATCH (key:Keyword) WHERE key.name='{0}' " \
                    "RETURN key".format(keyword_name)
            results = db.query(query, returns=(client.Node, str, client.Node))

        result = results.elements[0]

    except Exception as e:
        print('[Generate Keyword] Failed in storing keywords into Neo4j with error: {0}'.format(e.args[0]))
    return result


def get_date(current_date):
    """
    GET date
    :param current_date:
    :return:
    """
    date_node = db.labels.create("Date")  # date nodes
    result = False
    # Store keyword into Neo4j
    try:  # Check if keyword is existed
        query = "MATCH (dat:Date) WHERE dat.date='{0}' " \
                "RETURN dat".format(current_date)
        results = db.query(query, returns=(client.Node, str, client.Node))

        # Create new keywords
        if not results.elements:
            result = db.node.create(name=current_date)  # create keyword node
            date_node.add(result)

            query = "MATCH (dat:Date) WHERE dat.date='{0}' " \
                    "RETURN dat".format(current_date)
            results = db.query(query, returns=(client.Node, str, client.Node))

        result = results.elements[0]

    except Exception as e:
        print('[Generate Date] Failed in storing date into Neo4j with error: {0}'.format(e.args[0]))
    return result


# Get category in neo4j
def get_category_in_neo4j():
    """
    GET category from neo4j
    :return:
    """
    print("Getting categories in Neo4j")
    result = {}

    try:
        query = "MATCH (cat: Category) RETURN cat"
        data = db.query(query, returns=(client.Node, str, client.Node))
    except Exception as e:
        print('[Get Categories] Failed in getting categories from Neo4j with error: {0}'.format(e.args[0]))
        return False

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
            print('[Migrating Categories] Failed in storing categories into Neo4j with error: {0}'.format(e.args[0]))
            return False

    print("Getting categories from Neo4j successfully")

    for element in data:
        result[element[0]['name']] = element[0]  # add to category node array

    return result


def get_paper_by_category_and_date(category, from_date='0', to_date='0'):
    """
    GET paper by category and date
    :param category:
    :param from_date:
    :param to_date:
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
                "WHERE dat.date>'{1}' AND pap in paper " \
                "RETURN pap".format(category, from_date)
    try:
        return db.query(query, returns=(client.Node, str, client.Node))
    except Exception as e:
        print('get_paper_by_category_and_date] Failed in retrieving papers from neo4j: {0}'.format(e.args[0]))
        return False


# Create paper node
def create_paper_node(paper_title, paper, paper_sentences, category_nodes, current_category, current_date_node):
    """
    CREATE paper in Neo4j
    :param paper_title:
    :param paper:
    :param paper_sentences:
    :param category_nodes:
    :param current_category:
    :param current_date_node:
    :return:
    """
    result = {}
    result['code'] = False
    paper_nodes = db.labels.create("Paper")  # paper nodes
    try:
        # Save each paper to database
        current_paper_node = db.node.create(title=paper_title, path=paper, sentence=paper_sentences)
        paper_nodes.add(current_paper_node)  # update label for paper

        # create relationship from category to paper
        category_nodes[current_category].relationships.create("CategoryToPaper", current_paper_node)

        # create relationship from date to paper
        current_date_node.relationships.create("DateToPaper", current_paper_node)

        result['data'] = current_paper_node
        result['code'] = True
    except Exception as e:
        print('[create_paper_node] Failed storing at paper: {0} with errors: {1}'.format(paper_title, e.args[0]))

    return result


# Create date node
def create_date_node(current_date):
    """
    CREATE date in Neo4j
    :param current_date:
    """
    result = {}

    result['code'] = False
    date_nodes = db.labels.create("Date")  # date nodes
    try:
        current_date_node = db.node.create(date=current_date)
        date_nodes.add(current_date_node)

        result['code'] = True
        result['data'] = current_date_node

    except Exception as e:
        print('[create_date] Failed with error: {0}'.format(e.args[0]))

    return result


# load category
category_nodes = get_category_in_neo4j()
