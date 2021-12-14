<script>
    import Search from "svelte-search"
    import { SERVER, getAuthInfo, postJSON, getJSON } from '$lib/server'
    import ErrorMessage from "$lib/components/ErrorMessage.svelte"
    import LoginButton from "$lib/components/LoginButton.svelte"
    import LoginDialog from "$lib/components/LoginDialog.svelte"
    import { page } from '$app/stores'
    import Button, { Label, Icon } from '@smui/button'
import { log } from "loglevel"

    let value = ""

    let category = ( $page.query.has('category') 
        ? $page.query.get('category') 
        : 'general'
    )

    let query = $page.query.has('q') ? $page.query.get('q') : ""
    let page_no = $page.query.has('page') ? $page.query.get('page') : 1
    let searchError = undefined
    let searchInput

    async function getSearchResults(_query, _category, _page) {
        query = _query
        category = _category
        page_no = _page

        if (query) {
            window.history.pushState("", "", "/?q="+encodeURIComponent(value)+"&page="+page_no+"&category="+encodeURIComponent(category))
        }

        console.log("searching")

        return await getJSON(SERVER + '/api/search', {
            "q": query,
            "category": category,
            "page": page_no
        })
    }

    async function foundResult(searchResult) {
        let data = {page_no, category, query}
        let key
        for (key in searchResult) {
            data[key] = searchResult[key]
        }

        await postJSON(SERVER + "/api/found", data)
    }

    let authInfoData = getAuthInfo()

    let searchResultPromise

    function search(_query, _category, _page) {
        if (_query) {
            searchResultPromise = getSearchResults(_query, _category, _page)
        }
    }

    search(query, category, page_no)

</script>

<main>
    <div id="login-bar">
        {#await authInfoData}
            <p>Loading...</p>
        {:then authInfo}
            {#each Object.values(authInfo.auths) as auth }
                <LoginButton auth={auth} on:dialogClose={() => { console.log("searchInput", searchInput) ; searchInput.focus()} } />
            {/each}
        {:catch error}
            <ErrorMessage>{error}</ErrorMessage>
        {/await}

    </div>
    <div id="search-bar">
        <Search autofocus hideLabel label="Search" bind:value on:submit={search(value, category, page_no)} bind:this={searchInput} />
    </div>
    {#if query}
        <div id="search-results-container">
            {#await searchResultPromise}
                <p>Searching for "{query}"...</p>
            {:then searchResults}
                {#each searchResults.errors as error}
                    <ErrorMessage><b>{error.engine}</b>: {error.error}</ErrorMessage>
                {/each}
                    <div class="pager">
                        {#if page_no > 1}
                            <Button on:click={search(query, category, page_no-1)}><Label>Previous Page</Label></Button>
                        {/if}
                        <Button on:click={search(query, category, page_no+1)}><Label>Next Page</Label></Button>
                    </div>

                    <div id="search-results">
                        <p>There are about {searchResults.total} results</p>
                        {#each searchResults.results as searchResult}
                            <div class="search-result">
                                <!-- default -->
                                <cite class="url"><a href={searchResult.url} on:click={foundResult(searchResult)}>{searchResult.url}</a></cite>
                                <h3><a href={searchResult.url} on:click={foundResult(searchResult)}>{searchResult.title}</a></h3>
                                <div class="excerpt">{#if searchResult.published_at}<span class="publish-date">{new Date(searchResult.published_at).toISOString().split('T')}</span> &ndash; {/if}
                                    {#if searchResult.excerpt}
                                        {@html searchResult.excerpt.replaceAll(RegExp("("+query+")", 'ig'), (m) => `<b>${m}</b>`)}
                                    {/if}
                                    {#if searchResult.fields}
                                        {#each Object.entries(searchResult.fields) as [key, val]}
                                            <b>{key}</b>: {val}<br/>
                                        {/each}
                                    {/if}
                                </div>
                                <cite class="score">(Score {searchResult.score} (weights: {JSON.stringify(searchResult.weights)}, positions: {JSON.stringify(searchResult.positions)})</cite>

                            </div>

                        {/each}
                    </div>

                    <div class="pager">
                        {#if page_no > 1}
                            <Button on:click={search(query, category, page_no-1)}><Label>Previous Page</Label></Button>
                        {/if}
                        <Button on:click={search(query, category, page_no+1)}><Label>Next Page</Label></Button>
                    </div>
            {:catch error}
                <ErrorMessage>{error}</ErrorMessage>
            {/await}
        </div>
    {/if}
</main>

<style>
    #login-bar {
        text-align: center;
    }

    #search-bar, .pager {
        text-align: center;
    }

    #search-results-container {
        text-align: center;
    }

    #search-results {
        display: inline-block;
        text-align: left;
        width: 50%;
    }

    .search-result {
        margin-top: 2em;
    }

    .search-result h3 {
        font-weight: normal;
        font-size: 150%;
        margin-top: 0.1em;
        margin-bottom: 0.25em;
    }

    :global([data-svelte-search] input) {
        width: 50%;
        font-size: 1rem;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
        border-radius: 0.25rem;
    }

    cite.url a {
        color: #222;
        font-size: 90%;
        font-style: normal;
    }

    cite.score {
        color: #666;
        font-size: 75%;
    }

    .search-result .excerpt {
        color: #333;
    }



</style>
