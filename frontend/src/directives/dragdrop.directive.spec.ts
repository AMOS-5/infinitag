import { DragdropDirective } from './dragdrop.directive';
import {Component, DebugElement} from '@angular/core';
import {ComponentFixture, TestBed} from '@angular/core/testing';
import {By} from '@angular/platform-browser';

@Component({
    template: `<div class="dropzone" appDragdrop style="background-color:blue" (fileDropped)="onFileDropped($event)"></div>`
})
class TestDragDropComponent {
  public onFileDropped(fileList: FileList) {
    return null;
  }
}

describe('DragdropDirective', () => {
  let component: TestDragDropComponent;
  let fixture: ComponentFixture<TestDragDropComponent>;
  let div: DebugElement;

  const dragOverEvent: DragEvent = new DragEvent('dragover', null);
  const dragLeaveEvent: DragEvent = new DragEvent('dragleave', null);
  const file: File = new File([], 'file');

  const dropEvent = new CustomEvent('drop');
  dropEvent.initCustomEvent('drop', true, true, null);
  Object.defineProperty(dropEvent, 'dataTransfer', {
    value: {
      files: [file],
    },
    writable: true
  });


  beforeEach(() => {
        TestBed.configureTestingModule({
            declarations: [TestDragDropComponent, DragdropDirective]
        });
        fixture = TestBed.createComponent(TestDragDropComponent);
        component = fixture.componentInstance;
        div = fixture.debugElement.query(By.css('div'));
    });

  it('should create an instance', () => {
    const directive = new DragdropDirective();
    expect(directive).toBeTruthy();
  });

  it('drag enter and drag leave should change class of host element', () => {
        div.triggerEventHandler('dragover', dragOverEvent);
        fixture.detectChanges();
        expect(Object.keys(div.classes)).toContain('fileover');

        div.triggerEventHandler('dragleave', dragLeaveEvent);
        fixture.detectChanges();
        expect(Object.keys(div.classes)).not.toContain('fileover');
    });

  it('Should trigger event when dropped', () => {
    spyOn(component, 'onFileDropped');
    div.triggerEventHandler('drop', dropEvent);

    fixture.detectChanges();
    expect(component.onFileDropped).toHaveBeenCalled();
  });

});
