<script>
    import Search from "svelte-search"
    import { SERVER, getAuthInfo, postJSON } from '$lib/server'
    import ErrorMessage from "$lib/components/ErrorMessage.svelte"
    import LoginButton from "$lib/components/LoginButton.svelte"
    import LoginDialog from "$lib/components/LoginDialog.svelte"

    let value = ""
    let category = 'general'
    let searchError = undefined

    let searchResults = undefined
    let query = ""

    let page = 1

    async function getSearchResults(_query, _category, _page) {
        query = _query
        category = _category
        page = _page

        searchResults = undefined
        try {
            console.log("searching")
            searchResults = await getJSON(SERVER + '/api/search', {
                "q": query,
                "category": category,
                "page": page
            })

        } catch (error) {
            searchError = error
            console.log(error)
        }
    }

    async function foundResult(searchResult) {
        data = {page, category, query}
        for (key in searchResult) {
            data[key] = searchResult[key]
        }

        await postJSON(SERVER + "/api/found", data)
    }

    let authInfoData = getAuthInfo()

</script>

<main>
    <div id="login-bar">
        {#await authInfoData}
            <p>Loading...</p>
        {:then authInfo}
            {#each Object.values(authInfo.auths) as auth }
                <LoginButton auth={auth}/>
            {/each}
        {:catch error}
            <ErrorMessage>{error}</ErrorMessage>
        {/await}

    </div>
    <div id="search-bar">
        <Search autofocus hideLabel label="Search" bind:value on:submit={() => getSearchResults(value, category, page)}/>
            {#if query}
            <p>looking for {query}</p>
            {/if}

            {#if searchError}
            <p>{searchError}</p>
            {/if}
    </div>
    {#if searchResults}
    <div id="search-results-container">
        <div id="search-results">
            <p>There are about {searchResults.total} results</p>
            {#each searchResults.results as searchResult}
                {#if searchResult.type == 'page'}
                    <div class="search-result">
                        <cite class="url"><a href={searchResult.url} on:click={foundResult(searchResult)}>{searchResult.url}</a></cite>
                        <h3><a href={searchResult.url} on:click={foundResult(searchResult)}>{searchResult.title}</a></h3>
                        <div class="excerpt">{#if searchResult.published_at}<span class="publish-date">{new Date(searchResult.published_at).toISOString().split('T')}</span> &ndash; {/if}
                            {@html searchResult.excerpt.replaceAll(RegExp("("+query+")", 'ig'), (m) => `<b>${m}</b>`)}
                        </div>
                        <cite class="score">(Score {searchResult.score} (weights: {JSON.stringify(searchResult.weights)}, positions: {JSON.stringify(searchResult.positions)})</cite>
                    </div>
                {/if}
            {/each}
        </div>
    </div>
    {/if}
</main>

<style>
    #login-bar {
        text-align: center;
    }

    #search-bar {
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
