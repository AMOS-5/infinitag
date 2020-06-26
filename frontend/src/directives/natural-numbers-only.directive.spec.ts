import { NaturalNumbersOnlyDirective } from './natural-numbers-only.directive';
import { ElementRef } from '@angular/core';
import { TestBed, ComponentFixture } from '@angular/core/testing';
import { Component, HostListener } from '@angular/core';
import { By } from '@angular/platform-browser'



//Simple test component
@Component({
  template: '<input type="text" [(ngModel)]="data" appNaturalNumbersOnly>'
})
class TestComponent {
  data = ""
  constructor() { }
}

describe('naturalNumber directive', () => {
  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        TestComponent,
        NaturalNumbersOnlyDirective
      ]
    });

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;

    const directiveEl = fixture.debugElement.query(By.directive(NaturalNumbersOnlyDirective));
    expect(directiveEl).not.toBeNull();

    const directiveInstance = directiveEl.injector.get(NaturalNumbersOnlyDirective);
    expect(directiveInstance).not.toBeNull();

  });

  it('should create component', () => {
    expect(component).toBeDefined();
  });

  it('should not change input', () => {
    const debugEl: HTMLElement = fixture.debugElement.nativeElement;
    const input: HTMLInputElement = debugEl.querySelector('input');

    input.value = "55";
    fixture.detectChanges();
    var event = new Event('input', {});
    input.dispatchEvent(event);

    expect(input.value).toBe("55");
  });

  it('should not change empty input', () => {
    const debugEl: HTMLElement = fixture.debugElement.nativeElement;
    const input: HTMLInputElement = debugEl.querySelector('input');

    input.value = "";
    fixture.detectChanges();
    var event = new Event('input', {});
    input.dispatchEvent(event);

    expect(input.value).toBe("");
  });

  it('should remove letters', () => {
    const debugEl: HTMLElement = fixture.debugElement.nativeElement;
    const input: HTMLInputElement = debugEl.querySelector('input');

    input.value = "5a";
    fixture.detectChanges();
    var event = new Event('input', {});
    input.dispatchEvent(event);

    expect(input.value).toBe("5");
  });

  it('should change to 1', () => {
    const debugEl: HTMLElement = fixture.debugElement.nativeElement;
    const input: HTMLInputElement = debugEl.querySelector('input');

    input.value = "0";
    fixture.detectChanges();
    var event = new Event('input', {});
    input.dispatchEvent(event);

    expect(input.value).toBe("1");
  });
});