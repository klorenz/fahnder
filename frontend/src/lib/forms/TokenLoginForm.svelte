<script>
    import Form from "$lib/components/Form.svelte"
    import Textfield from '@smui/textfield';
    import Icon from '@smui/textfield/icon';

    let postData = {'token': ''}

    function handleFormResponse() {
        localStorage.setItem(`${auth.name}_username`, postData['username'])
        localStorage.setItem(`${auth.name}_password`, postData['password'])

        auth.logged_in = true
    }

</script>

<Form bind:postData>
    <Textfield variant="outlined" label="Token" bind:value={postData['token']}>
        <Icon class="material-icons" slot="leadingIcon">key</Icon>
    </Textfield>
</Form>
