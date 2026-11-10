"""Local inline icons: no font, script or remote request required."""
import html


def social_icon(network):
    paths = {
        'instagram': '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1.2"/>',
        'youtube': '<path d="M22 8a4 4 0 0 0-3-3c-3-.4-11-.4-14 0a4 4 0 0 0-3 3 27 27 0 0 0 0 8 4 4 0 0 0 3 3c3 .4 11 .4 14 0a4 4 0 0 0 3-3 27 27 0 0 0 0-8Z m-12 0 6 4-6 4Z" fill-rule="evenodd"/>',
        'facebook': '<path d="M14 22v-9h3l.5-4H14V7c0-1 .3-2 2-2h2V1.5C17 1.2 16 1 15 1c-3 0-5 2-5 5v3H7v4h3v9Z"/>',
    }
    return '<svg class="social-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">'+paths[network]+'</svg>'


def social_link(url, network, label, css=''):
    esc = lambda value: html.escape(str(value), quote=True)
    return f'<a class="social-icon-link {esc(css)}" href="{esc(url)}" aria-label="{esc(label)}" title="{esc(label)}" data-social="{network}">'+social_icon(network)+'</a>'
