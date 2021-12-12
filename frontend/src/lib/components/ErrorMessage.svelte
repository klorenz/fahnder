<script>
    import Paper, { Title, Content } from '@smui/paper'
    export let title = "Error"
</script>

<Paper variant="outlined">
    {#if title !== null}
        <Title>{title}</Title>
    {/if}
    <Content><slot/></Content>
</Paper>
