<script>
    import TokenLoginForm from '$lib/forms/TokenLoginForm.svelte';
    import UserPasswordLoginForm from '$lib/forms/UserPasswordLoginForm.svelte'
    import { onMount, createEventDispatcher } from 'svelte'
    import Dialog, { Content, Title, Actions } from '@smui/dialog'
    import logging from '$lib/logging'

    let logger = logging.getLogger('LoginDialog')

    export let open = false
    export let auth = {}

    const dispatch = createEventDispatcher()

    function closeDialog() {
        logger.debug("closeDialog")
        dispatch('close')
        open = false
    }

    $: logger.debug("dialog state", open)

</script>

<Dialog bind:open
    aria-labelledby="dialog-{auth.name}-title"
    aria-describedby="dialog-{auth.name}-content"
>
    <Title id="dialog-{auth.name}-title">Login to {auth.name}</Title>
    <Content id="dialog-{auth.name}-content">
        {#if auth.type == "basic"}
            <UserPasswordLoginForm auth={auth} on:response={closeDialog} on:cancel={closeDialog} hasCancel={true}/>
        {:else if auth.type == "token"}
            <TokenLoginForm auth={auth} on:response={closeDialog} on:cancel={closeDialog} hasCancel={true}/>
        {:else}
            <p>Unsupported Auth type: {auth.type}</p>
        {/if}
    </Content>
</Dialog>
