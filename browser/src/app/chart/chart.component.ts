import { Component, OnInit, Input , AfterContentChecked, AfterContentInit} from '@angular/core';
import type { EChartsOption } from 'echarts';
import { NgxEchartsDirective, provideEcharts } from 'ngx-echarts';
import { dataPoint } from '../interfaces';
import {formatDate} from '@angular/common';

@Component({
  selector: 'app-chart',
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.scss'],
  providers: [provideEcharts()]
})

export class ChartComponent implements AfterContentChecked{

  @Input() data: dataPoint[] = [];
  @Input() title: string = "";
  @Input() yAxisLabel: string = "";
  @Input() eletricity: boolean = false;

  
  options: EChartsOption = {};

  constructor() {}

  ngAfterContentChecked(): void {
    const xAxisData: string[] = [];
    const chartData: number[] = [];
    const barBackgrounds: string[] = [];
    const yAxisLabel: string = this.yAxisLabel;
    const elec = this.eletricity;

    for (const dataPoint of this.data)
    {
      let axisTitleHour: string = formatDate(dataPoint.date, 'HH', 'en-FI');
      chartData.push(dataPoint.value)

      let backgound: string = 'transparent';
      if (formatDate(new Date(), 'dd.H', 'en-FI') == formatDate(dataPoint.date, 'dd.H', 'en-FI'))
      {
          axisTitleHour = axisTitleHour + '\nNow'
      }
      xAxisData.push(axisTitleHour)
      barBackgrounds.push(backgound)
    }

    this.options = {
      title: {
        left: 'center',
        text: this.title
      },

      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        name: "Time",
        data: xAxisData,
        silent: false,
        axisTick: {
          show: true,
          interval: 0
        },
        splitLine: {
          show: true,
          interval: 0
        },
        axisLabel: {
          align: 'center',
          overflow: 'break'
        },
        nameTextStyle: {
          fontSize: 14,
        }
      },
      yAxis: {
        name: yAxisLabel,
        nameTextStyle: {
            fontSize: 14,
        }
      },
      series: [
        {
          type: 'bar',
          barCategoryGap: "7-5%",
          data: chartData,
          animationDelay: idx => idx * 10,
          showBackground: false,
          itemStyle: {
            color(params) {
              if (params.name.endsWith("Now"))
              {
                return '#4169E1'
              }
              if (params.name === "00"){
                return 'grey'
              }
              if (elec) 
              {
                let value: number = Number(params.value);
                if (value < 10) {
                  return '#4CAF50'
                }
                else if (10 < value && value < 20) {
                  return '#FFC107'
                }
                else {
                  return '#FF5252'
                }
              }
              return '#3498db'
            },
          },
        },

      ],
      animationEasing: 'elasticOut',
      animationDelayUpdate: idx => idx * 5,
    };
  }
}
