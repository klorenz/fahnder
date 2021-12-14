import logging from '$lib/logging'

const logger = logging.getLogger('server')

export const SERVER = import.meta.env.VITE_SERVER

export let pageAuth = null

export async function getJSON(url, data) {
    let query = ""
    for (let k in data) {
        query += '&'+k+'='+encodeURI(data[k])
    }
    if (query !== "") {
        query = '?'+query.substring(1)
    }

    const response = await fetch(`${url}${query}`, {
        method: "GET",
        credentials: SERVER.match(/localhost/) ? 'include' : 'same-origin',
    })

    const responseData = await response.json()

    if (response.ok) {
        return responseData
    // } else {
        // if (response.status == 401) {


        // }
    }

    throw new Error(`Status ${response.status}: ${responseData.error}`)
}

export async function postJSON(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: SERVER.match(/localhost/) ? 'include' : 'same-origin',

        body: JSON.stringify(data)
    })
    const responseData = await response.json()

    if (response.ok) {
        return responseData
    }

    throw new Error(`Status ${response.status}: ${responseData.error}`)
}

export async function getAuthInfo() {
    const result = await getJSON(SERVER + '/api/auth_info')
    logger.debug('getAuthInfo', result)

    pageAuth = result.auths[result.auth]
    logger.debug('pageAuth', pageAuth)

    return result
}

export function logIn(auth) {
    document.location = `${SERVER}/login/${auth.name}`
}

export async function logOut(auth) {
    // await fetch(`:w logout
    // ${})
    document.location = `${SERVER}/login/${engine}`
    //if ()
    document.cookie = `${engine}_name=; Max-Age=0`;
    document.cookie = `${engine}_username=; Max-Age=0`;
    document.cookie = `${$ngine}_access_token=; Max-Age=0`;
}
