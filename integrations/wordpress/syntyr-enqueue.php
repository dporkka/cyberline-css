<?php
/**
 * Example for a WordPress child theme's functions.php.
 * Copy the source-candidate dist/syntyr.embed.css into child theme assets.
 * This is integration guidance, not a bundled, supported WordPress plugin.
 */
if (!function_exists('syntyr_child_theme_enqueue_embed_example')) {
    function syntyr_child_theme_enqueue_embed_example(): void {
        $relative = '/assets/syntyr.embed.css';
        $absolute = get_stylesheet_directory() . $relative;
        if (!is_readable($absolute)) {
            return;
        }
        wp_enqueue_style(
            'syntyr-embed',
            get_stylesheet_directory_uri() . $relative,
            array(),
            (string) filemtime($absolute)
        );
    }
}
add_action('wp_enqueue_scripts', 'syntyr_child_theme_enqueue_embed_example');
add_action('enqueue_block_editor_assets', 'syntyr_child_theme_enqueue_embed_example');
