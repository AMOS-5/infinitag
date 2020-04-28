import {Component, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  public title = 'infinitag';
  public serverUrl = 'http://localhost:8080';
  public backendStatus = `${this.serverUrl}/health`;

  public serverStatus = 'DOWN';

  constructor( private httpClient: HttpClient) {}

  public ngOnInit(): void {
    this.httpClient.get(this.backendStatus)
      .subscribe((value: {status: string}) => {
        this.serverStatus = value.status;
      });
  }
}
