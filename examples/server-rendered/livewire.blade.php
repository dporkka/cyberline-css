{{-- Copy into a Laravel Livewire 4 Blade view; component supplies $name and save().
     For Livewire 3, use wire:loading or wire:loading.attr on elements needing a busy state. --}}
<section class="syn-root" data-syn-theme="studio">
    <article class="syn-panel">
        <h2 class="syn-heading">New campaign</h2>
        <form class="syn-form" wire:submit="save">
            <div class="syn-field">
                <label class="syn-label" for="campaign-name">Campaign name</label>
                <input id="campaign-name" name="name" class="syn-input"
                       wire:model.live="name"
                       aria-invalid="{{ $errors->has('name') ? 'true' : 'false' }}"
                       @error('name') aria-describedby="campaign-name-error" @enderror>
                @error('name')
                    <p id="campaign-name-error" class="syn-error">{{ $message }}</p>
                @enderror
            </div>
            <button type="submit" class="syn-button syn-button--primary">Save campaign</button>
        </form>
    </article>
</section>
