<script>
    import Card, {
        Content,
        PrimaryAction,
        Actions,
        ActionButtons,
        ActionIcons,
    } from '@smui/card'
    import { postJSON } from '$lib/server'
    import Button, { Label } from '@smui/button'
    import { createEventDispatcher } from 'svelte'
    import ErrorMessage from './ErrorMessage.svelte'
    import logging from '$lib/logging'

    const logger = logging.getLogger('Form')

    const dispatch = createEventDispatcher()

    export let postData = {}
    export let hasCancel = false
    export let postUrl = ""

    let error = ""

    async function handleSubmit() {
        logger.debug("handleSubmit", postData)

        try {
            const data = await postJSON(postUrl, postData)
            dispatch('response', data)
        } catch (err) {
            error = err
        }
    }

    function handleCancel() {
        logger.debug("handleCancel")
        dispatch('cancel')
        return false
    }
</script>

<form on:submit|preventDefault={handleSubmit}>
    <Card>
        <Content>
            <div>
                <slot></slot>
            </div>
            {#if error !== ""}
                <ErrorMessage>{error}</ErrorMessage>
            {/if}
        </Content>

        <Actions>
            <ActionButtons>
                <Button type="submit">Submit</Button>
                {#if hasCancel}
                    <Button type="button" on:click={handleCancel}>Cancel</Button>
                {/if}
            </ActionButtons>
        </Actions>
    </Card>
</form>
