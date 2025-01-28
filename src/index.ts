import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ICommandPalette } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';

import { requestAPI } from './handler';

/**
 * Initialization data for the jupyter_exam extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter_exam:plugin',
  description: 'A JupyterLab extension to collect exam files',
  autoStart: true,
  requires: [ICommandPalette, INotebookTracker],
  optional: [ISettingRegistry],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    nbtracker: INotebookTracker,
    settingRegistry: ISettingRegistry | null
  ) => {
    console.log('JupyterLab extension jupyter_exam is activated!');

    const { commands } = app;

    commands.addCommand('jupyter-exam:submit', {
      label: 'Submit Exam',
      caption: 'Submit the exam to the server',
      execute: (args: any) => {
        const current = nbtracker.currentWidget;
        if (!current) {
          console.error('No notebook is active');
          return;
        }
        const panel = current.content;
        const nbData = panel.model?.toJSON();
        console.log(nbData);

        console.log(JSON.stringify(args));
        requestAPI<any>('submit', {
          body: JSON.stringify({ notebook: nbData }),
          method: 'POST'
        })
          .then(data => {
            console.log(data);
          })
          .catch(reason => {
            console.error(
              `The jupyter_exam server extension appears to be missing.\n${JSON.stringify(reason)}`
            );
          });
      }
    });
    palette.addItem({
      command: 'jupyter-exam:submit',
      category: 'Notebook Operations'
    });

    nbtracker.currentChanged.connect((_, nbPanel) => {
      if (!nbPanel) {
        return;
      }
      nbPanel.context.saveState.connect((_, state) => {
        if (state === 'completed') {
          commands.execute('jupyter-exam:submit');
        }
      });
    });

    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('jupyter_exam settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error('Failed to load settings for jupyter_exam.', reason);
        });
    }
  }
};

export default plugin;
