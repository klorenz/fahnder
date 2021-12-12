<script>
    import { SERVER } from '$lib/server'
    import Button from '@smui/button'
    export let auth = {}

    function logIn() {
        document.location = `${SERVER}/login/${auth.name}`
    }
</script>

<Button on:click={logIn()}>Login with <span class="auth-name">{auth.name}</span></Button>

<style>
</style>
