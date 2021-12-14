from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import get_sha
from .models.interests import store_interest
from .models.queries import store_query
from .search_request import SearchRequest
from flask import g
from math import sqrt, log2
import traceback

def search(request: SearchRequest):
    # may already exist res.get('status') == 409

    # store query for completion
    store_query(request.query)
    store_interest('search', vars(request))

    # initialize search result
    search_result = {
        'total': 0,
        'page': request.page,
        'errors': []
        }

    # a dictionary by url, such that we can aggregate duplicate results from 
    # muliple search engines
    results = {}

    # find elevant engines, i.e. engines serving queried category
    relevant_engines = []
    for engine in g.engines.values():
        if request.category not in engine.categories:
            continue

        relevant_engines.append(engine)

    # query all search engines at the same time
    # see https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example
    with ThreadPoolExecutor(max_workers=len(relevant_engines)) as executor:
        promises = {
            executor.submit(engine.search, request)
            : engine for engine in relevant_engines
            }

    # wait for promises and iterate over them
    for promise in as_completed(promises):
        engine = promises[promise]
        try:
            engine_result = promise.result()
        except Exception as exc:
            print("%r generated an exception: %r" % (engine, exc))
            traceback.print_exc()

            search_result['errors'].append(dict(
                error = str(exc),
                engine = engine.name,
            ))

            continue

        # process results
        for (i, result) in enumerate(engine_result['results'], start=1):

            # get result's weight
            weight = result.get('weight', engine.weight)

            # initialize new result, if not yet there
            if result['url'] not in results:
                print(f"add result with {result['url']}")
                results[result['url']] = result
                result['positions'] = []
                result['weights'] = []
                result['engines'] = []
            else:
                print(f"have result with {result['url']}")
                result = results[result['url']]
                # TODO: need to assert same type??

            result['engines'].append(engine.name)

            print("result:", result)

            # append position in engine's results
            result['positions'].append(i)

            # append result's weight
            result['weights'].append(weight)

        # aggregate totals
        search_result['total'] += engine_result['total']

    # finally iterate over results, calculate scores and pick out special results
    for result in results.values():

        # calclulate score
        result['score'] = result_score(result, len(results))

        # if title is same like query, this is most probably the answer
        if result['title'].lower() == request.query.lower():
            # todo ask engine to get the content of this doc
            search_result['answer'] = result

    # sort by score, 
    search_result['results'] = list(reversed(sorted(results.values(), key=lambda r: r['score'])))
    return search_result

def result_score(result, max_docs):
    # scoring is only done within a page to order the docs
    #
    # see https://www.compose.com/articles/how-scoring-works-in-elasticsearch/
    #
    # Those docs are more important, which
    #
    # - Have a higher avarage position in their engine's results
    # - Have a higher weight of engines

    position = sum(result['positions'])/len(result['positions'])
    engine_weight = sum(result['weights'])/sqrt(len(result['weights']))

    return 1-1/(position*engine_weight)

