const { exec } = require('child_process');

// تثبيت المكتبة اللازمة
exec('npm install -g nodemon', (error, stdout, stderr) => {
  if (error) {
    console.error(`Error installing nodemon: ${error.message}`);
    return;
  }
  
  // تنفيذ الكود باستخدام nodemon
  const nodemonProcess = exec('nodemon main.js');

  // معالجة الأخطاء
  nodemonProcess.on('error', (error) => {
    console.error(`Error running nodemon: ${error.message}`);
  });

  // معالجة إغلاق العملية
  nodemonProcess.on('close', (code) => {
    console.log(`nodemon process exited with code ${code}`);
    
    // إعادة تشغيل الكود في حالة التوقف
    if (code !== 0) {
      console.log('Restarting nodemon...');
      exec('nodemon main.js');
    }
  });
});
