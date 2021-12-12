<script>
    import Button, { Label, Icon } from '@smui/button'
    import { SERVER } from '$lib/server'
    import { onMount } from 'svelte'
    import logging from '$lib/logging'
    import LoginDialog from '$lib/components/LoginDialog.svelte' 

    const logger = logging.getLogger("LoginButton")

    export let auth = {}

    let dialogOpen = false

    function loginLogout() {
        if (auth.logged_in) {
            document.location = `${SERVER}/logout/${auth.name}`
        } else {
            if (auth.type === "oauth") {
                document.location = `${SERVER}/login/${auth.name}`
            } else {
                dialogOpen = true
            }
        }
    }

    // onMount(() => {
    //     logger.debug("auth", auth, "dialog closed", auth.name)
    // })


</script>

<Button variant="outlined" on:click={loginLogout}>
    <Icon class="material-icons">
        {#if auth.logged_in}
            lock_open
        {:else}
            lock
        {/if}
    </Icon>
    <Label>{auth.name}</Label>

</Button>

{#if auth.type !== "oauth"}
    <LoginDialog auth={auth} bind:open={dialogOpen} />
{/if}
