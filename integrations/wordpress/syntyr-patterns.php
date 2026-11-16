<?php
/**
 * Plugin Name: Syntyr Native Block Patterns (example)
 * Description: Three opt-in, editable Gutenberg patterns using WordPress core blocks.
 * Version: 0.1.0
 * License: MIT
 *
 * This adapter supplies patterns only. The child theme owns pinned Syntyr CSS.
 * Do not require it as part of Syntyr's framework-neutral distribution.
 */
defined('ABSPATH') || exit;

add_action('init', static function (): void {
    if (!function_exists('register_block_pattern') ||
        !function_exists('register_block_pattern_category')) {
        return;
    }
    register_block_pattern_category('syntyr', array(
        'label' => __('Syntyr Sections', 'syntyr-patterns'),
    ));
    $patterns = array(
        'service-overview' => array('Services overview', 'Three editable service cards'),
        'article-teasers' => array('Latest articles', 'Editorial heading and live post list'),
        'call-to-action' => array('Contact call to action', 'A direct action section'),
    );
    foreach ($patterns as $slug => $meta) {
        $file = __DIR__ . '/patterns/' . $slug . '.html';
        if (!is_readable($file)) {
            continue;
        }
        $content = file_get_contents($file);
        if ($content === false || $content === '') {
            continue;
        }
        register_block_pattern('syntyr/' . $slug, array(
            'title' => $meta[0],
            'description' => $meta[1],
            'categories' => array('syntyr'),
            'content' => $content,
        ));
    }
});
