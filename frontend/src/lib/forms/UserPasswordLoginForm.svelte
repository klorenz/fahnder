<script>
    import Form from "$lib/components/Form.svelte"
    import Textfield from '@smui/textfield';
    import Icon from '@smui/textfield/icon';
    import { SERVER } from '$lib/server'
    import { createEventDispatcher } from 'svelte'

    export let hasCancel = false

    export let auth = {}

    let postData = {
        'username': '',
        'password': ''
    }

    const dispatch = createEventDispatcher()

    function handleFormResponse() {
        location.reload()
    }

</script>

<Form bind:postData on:response={handleFormResponse} on:cancel hasCancel={hasCancel} postUrl={`${SERVER}/login/basic/${auth.name}`}>
    <p>
    <Textfield variant="outlined" label="Username" bind:value={postData['username']}>
        <Icon class="material-icons" slot="leadingIcon">person</Icon>
    </Textfield>
    </p>
    <p>
    <Textfield variant="outlined" label="Password" type="password" bind:value={postData['password']}>
        <Icon class="material-icons" slot="leadingIcon">password</Icon>
    </Textfield>
    </p>

</Form>
