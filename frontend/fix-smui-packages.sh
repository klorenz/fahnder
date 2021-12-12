for f in $(find node_modules/@smui -name package.json) ; do
    echo $f
    mv $f $f.old
    cat $f.old | jq '.main = "dist/index.js" | .svelte = "dist/index.js"' > $f
    rm $f.old
done
