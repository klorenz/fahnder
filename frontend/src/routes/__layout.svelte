<script>

//    import { page } from "$app/stores";
    import { onMount } from "svelte";
    import { getAuthInfo, logIn, logOut, pageAuth } from "$lib/server";
    import { user, initStores } from "$lib/store.js";
    import Index from "./index.svelte";
    import ErrorMessage from '$lib/components/ErrorMessage.svelte'
    import OAuthLoginForm from '$lib/forms/OAuthLoginForm.svelte'
    import TokenLoginForm from '$lib/forms/TokenLoginForm.svelte'
    import UserPasswordLoginForm from "$lib/forms/UserPasswordLoginForm.svelte";
    import logging from '$lib/logging'

    const logger = logging.getLogger('__layout')

    onMount(async () => {
        initStores();
        logger.debug("$user", $user)
    });

    let authInfoData = getAuthInfo()
</script>

{#await authInfoData}
  <p>Loading...</p>
{:then authInfo}
  {#if authInfo.auth === null || $user}
    <slot/>
  {:else}
    <!-- login forms here -->
    {#if pageAuth.type == 'oauth'}
      <OAuthLoginForm auth={pageAuth}/>
    {:else if pageAuth.type == 'basic'}
      <UserPasswordLoginForm auth={pageAuth}/>
    {:else if pageAuth.type == 'token'}
      <TokenLoginForm auth={pageAuth}/>
    {:else}
      <ErrorMessage>Cannot handle auth type {pageAuth.type}</ErrorMessage>
    {/if}
  {/if}
{:catch error}
  <ErrorMessage>{error}</ErrorMessage>
{/await}
