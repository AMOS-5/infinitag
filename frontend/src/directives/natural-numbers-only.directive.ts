import { Directive, ElementRef, HostListener } from '@angular/core';


/**
 * @class NaturalNumbersOnlyDirective
 *
 * Directive that ensures that the associated input field only
 * contains positiv integers
 */
@Directive({
  selector: '[appNaturalNumbersOnly]'
})
export class NaturalNumbersOnlyDirective {

  constructor(private _el: ElementRef) { }

  @HostListener('input', ['$event']) onInputChange(event) {
    const initalValue = this._el.nativeElement.value;
    let replaced = initalValue.replace(/[^0-9]*/g, '');
    if(replaced !== '' && Number(replaced) < 1) {
      replaced = "1";
    }
    this._el.nativeElement.value = replaced;

    if(initalValue !== this._el.nativeElement.value) {
      event.stopPropagation();
    }
  }
}
